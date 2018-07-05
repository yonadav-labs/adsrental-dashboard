import datetime
import decimal

from django.shortcuts import render, Http404
from django.views import View
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from adsrental.models.lead_history_month import LeadHistoryMonth
from adsrental.models.bundler import Bundler


class BundlerCheckView(View):
    @method_decorator(login_required)
    def get(self, request, bundler_id):
        now = timezone.localtime(timezone.now())

        select_dates = []
        for months_ago in range(3, 0, -1):
            select_dates.append((now.replace(day=1) - relativedelta(months=months_ago)).date())

        date_str = request.GET.get('date', select_dates[-1].strftime(settings.SYSTEM_DATE_FORMAT))
        date = datetime.datetime.strptime(date_str, settings.SYSTEM_DATE_FORMAT).date()

        bundler = Bundler.objects.filter(id=int(bundler_id)).first()
        if not bundler:
            raise Http404

        if not request.user.is_superuser and request.user.bundler != bundler:
            raise Http404

        lead_histories = LeadHistoryMonth.objects.filter(
            lead__bundler=bundler,
            date=date,
            move_to_next_month=False,
        ).select_related('lead', 'lead__raspberry_pi')
        total = decimal.Decimal('0.00')
        for lead_history in lead_histories:
            total += lead_history.get_remaining_amount()

        return render(request, 'bundler_report_check.html', context=dict(
            lead_histories=lead_histories,
            bundler=bundler,
            date_formatted=date.strftime('%B %Y'),
            date=date,
            select_dates=select_dates,
            total=total,
        ))
