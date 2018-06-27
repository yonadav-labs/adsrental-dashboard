import datetime

from django.views import View
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.humanize.templatetags.humanize import naturaltime

from adsrental.models.lead import Lead
from adsrental.models.lead_history import LeadHistory
from adsrental.models.lead_history_month import LeadHistoryMonth


class UserStatsView(View):
    def get(self, request):
        leadid = request.session.get('leadid')
        lead = Lead.objects.filter(leadid=leadid).first()
        if not lead:
            return redirect('user_login')

        return render(request, 'user/stats.html', dict(
            lead=lead,
            lead_accounts=lead.lead_accounts.all(),
            raspberry_pi=lead.raspberry_pi,
            raspberry_pi_offline_since=naturaltime(lead.raspberry_pi.last_seen) if lead.raspberry_pi and lead.raspberry_pi.last_seen else '',
            lead_histories=LeadHistory.objects.filter(lead=lead, date__gte=timezone.now().date() - datetime.timedelta(days=30)).order_by('-date'),
            lead_histories_month=LeadHistoryMonth.objects.filter(lead=lead).order_by('-date'),
        ))
