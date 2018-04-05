import datetime
import json

from django.shortcuts import render, Http404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models.functions import TruncDay
from django.db.models import Count
from django.utils import timezone, dateformat

from adsrental.models.lead_account import LeadAccount


class BundlerReportView(View):
    @method_decorator(login_required)
    def get(self, request):
        bundler = request.user.bundler
        # if not bundler:
        #     raise Http404

        lead_accounts = LeadAccount.objects.filter(qualified_date__isnull=False)
        if bundler:
            lead_accounts = lead_accounts.filter(lead__bundler=bundler)

        lead_accounts_by_date = (
            lead_accounts
            .annotate(date=TruncDay('qualified_date'))
            .values('date') 
            .annotate(count=Count('id')) 
            .values_list('date', 'count') 
        )
        lead_accounts_by_date_dict = {}
        for dt, value in lead_accounts_by_date:
            lead_accounts_by_date_dict[dt.date()] = value

        entries = []
        now = timezone.now()
        for i in range(30):
            date = (now - datetime.timedelta(days=i)).date()
            value = lead_accounts_by_date_dict.get(date, 0)
            entries.append([dateformat.format(date, 'jS F'), value])

        entries.reverse()

        # raise ValueError(entries)

        return render(request, 'bundler_dashboard.html', dict(
            user=request.user,
            bundler=bundler,
            entries=entries,
            entries_keys_json=json.dumps([k for k, v in entries]),
            entries_values_json=json.dumps([v for k, v in entries]),
        ))
