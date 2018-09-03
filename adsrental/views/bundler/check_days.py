import datetime
import decimal
from dateutil import parser, relativedelta

from django.shortcuts import render, Http404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone

from adsrental.models.lead_history import LeadHistory
from adsrental.models.bundler import Bundler
from adsrental.models.lead import Lead
from adsrental.utils import get_month_boundaries_for_dt


class BundlerCheckDaysView(View):
    @method_decorator(login_required)
    def get(self, request, bundler_id, lead_id):
        now = timezone.localtime(timezone.now())
        date_str = request.GET.get('date')
        if date_str:
            date = parser.parse(date_str).replace(tzinfo=timezone.get_current_timezone())
        else:
            date = now

        current_month_start, _ = get_month_boundaries_for_dt(date)
        start_date, end_date = get_month_boundaries_for_dt(current_month_start - datetime.timedelta(days=1))

        bundler = Bundler.objects.filter(id=int(bundler_id)).first()
        lead = Lead.objects.get(leadid=lead_id)
        if not bundler:
            raise Http404

        if not request.user.is_superuser and request.user.bundler != bundler:
            raise Http404

        lead_histories = LeadHistory.objects.filter(
            lead__bundler=bundler,
            date__gte=start_date,
            date__lte=end_date,
            lead=lead,
        ).select_related('lead', 'lead__raspberry_pi')
        total = decimal.Decimal('0.00')
        for lead_history in lead_histories:
            lead_history.amount, lead_history.note = lead_history.get_amount_with_note()
            total += lead_history.amount

        return render(request, 'bundler_report_check_days.html', context=dict(
            lead_histories=lead_histories,
            lead=lead,
            bundler=bundler,
            start_date=start_date,
            end_date=end_date,
            total=total,
        ))
