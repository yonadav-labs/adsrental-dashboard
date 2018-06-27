from django.views import View
from django.shortcuts import render, redirect
from django.contrib.humanize.templatetags.humanize import naturaltime

from adsrental.models.lead import Lead


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
        ))
