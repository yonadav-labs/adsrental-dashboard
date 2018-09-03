import datetime
from dateutil import parser

from django.utils import timezone
from django.views import View
from django.shortcuts import render, redirect

from adsrental.models.lead import Lead
from adsrental.models.lead_history import LeadHistory


class UserTimestampsView(View):
    @staticmethod
    def last_day_of_month(any_day):
        next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
        return next_month - datetime.timedelta(days=next_month.day)

    def get(self, request):
        leadid = request.session.get('leadid')
        lead = Lead.objects.filter(leadid=leadid).first()
        if not lead:
            return redirect('user_login')

        now = timezone.localtime(timezone.now())
        date_str = request.GET.get('date')
        if date_str:
            date = parser.parse(date_str).replace(tzinfo=timezone.get_current_timezone())
        else:
            date = now

        date_start = date.replace(day=1)
        date_end = self.last_day_of_month(date)

        lead_histories = LeadHistory.objects.filter(
            lead=lead,
            date__gte=date_start,
            date__lte=date_end,
        ).order_by('-date')

        for lh in lead_histories:
            lh.amount, _ = lh.get_amount_with_note()

        return render(request, 'user/timestamps.html', dict(
            lead=lead,
            lead_accounts=lead.lead_accounts.all(),
            date_start=date_start,
            date_end=date_end,
            raspberry_pi=lead.raspberry_pi,
            lead_histories=lead_histories,
        ))
