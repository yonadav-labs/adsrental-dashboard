import datetime
import json

from django.shortcuts import render, Http404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Count
from django.utils import timezone

from adsrental.models.bundler import Bundler
from adsrental.models.lead_account import LeadAccount
from adsrental.models.bundler_lead_stat import BundlerLeadStat


class BundlerLeaderboardView(View):
    @method_decorator(login_required)
    def get(self, request, bundler_id):
        bundler = None
        if request.user.bundler:
            bundler = request.user.bundler

        if request.user.is_superuser:
            bundler = Bundler.objects.filter(id=bundler_id).first()

        if not bundler:
            raise Http404

        top_bundlers_ids_list = BundlerLeadStat.objects.filter(bundler__is_active=True).exclude(bundler_id=bundler.id).order_by('-in_progress_total').values_list('bundler_id')
        bundler_ids = [bundler.id, ]
        for bundler_id in top_bundlers_ids_list:
            bundler_ids.append(bundler_id)

        current_bundler_lead_stat = BundlerLeadStat.objects.filter(bundler=bundler).first()
        current_rank = None

        now = timezone.localtime(timezone.now())
        lead_accounts = LeadAccount.objects.filter(
            qualified_date__isnull=False,
            account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK,
            lead__bundler__utm_source__isnull=False,
            primary=True,
        )

        lead_accounts_last_month = (
            lead_accounts
            .filter(qualified_date__gt=now - datetime.timedelta(days=31))
            .values('lead__bundler__utm_source')
            .annotate(count=Count('id'))
            .order_by('lead__bundler__utm_source')
            .values_list('lead__bundler__utm_source', 'count')
        )

        lead_accounts_last_week = (
            lead_accounts
            .filter(qualified_date__gt=now - datetime.timedelta(days=7))
            .values('lead__bundler__utm_source')
            .annotate(count=Count('id'))
            .order_by('lead__bundler__utm_source')
            .values_list('lead__bundler__utm_source', 'count')
        )

        lead_accounts_today = (
            lead_accounts
            .filter(qualified_date__gt=now.replace(hour=0, minute=0, second=0))
            .values('lead__bundler__utm_source')
            .annotate(count=Count('id'))
            .order_by('lead__bundler__utm_source')
            .values_list('lead__bundler__utm_source', 'count')
        )

        lead_accounts_yesterday = (
            lead_accounts
            .filter(
                qualified_date__lt=now.replace(hour=0, minute=0, second=0),
                qualified_date__gt=now.replace(hour=0, minute=0, second=0) - datetime.timedelta(days=1),
            )
            .values('lead__bundler__utm_source')
            .annotate(count=Count('id'))
            .order_by('lead__bundler__utm_source')
            .values_list('lead__bundler__utm_source', 'count')
        )

        lead_accounts_today_total = 0

        lead_accounts_today_sorted = sorted(list(lead_accounts_today), key=lambda x: x[1], reverse=True)
        for index, value in enumerate(lead_accounts_today_sorted):
            lead_accounts_today_total += value
            if bundler.utm_source == value[0] and value[0]:
                current_rank = index + 1

        return render(request, 'bundler_leaderboard.html', dict(
            user=request.user,
            bundler=bundler,
            bundler_lead_stat=current_bundler_lead_stat,
            rank=current_rank,
            month_entries_json=json.dumps(list(lead_accounts_last_month)),
            week_entries_json=json.dumps(list(lead_accounts_last_week)),
            today_entries_json=json.dumps(list(lead_accounts_today)),
            yesterday_entries_json=json.dumps(list(lead_accounts_yesterday)),
            lead_accounts_today_total=lead_accounts_today_total,
        ))
