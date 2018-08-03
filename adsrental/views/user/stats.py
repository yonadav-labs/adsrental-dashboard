from django.views import View
from django.shortcuts import render, redirect

from adsrental.models.lead import Lead
from adsrental.models.lead_history_month import LeadHistoryMonth


class UserStatsView(View):
    def get(self, request):
        leadid = request.session.get('leadid')
        if not leadid:
            return redirect('user_login')
        lead = Lead.objects.filter(leadid=leadid).first()
        if not lead:
            return redirect('user_login')

        if not lead.is_active():
            return render(request, 'user/stats_banned.html', dict(
                lead=lead,
            ))

        return render(request, 'user/stats.html', dict(
            lead=lead,
            lead_accounts=lead.lead_accounts.all(),
            raspberry_pi=lead.raspberry_pi,
            lead_histories_month=LeadHistoryMonth.objects.filter(lead=lead).order_by('-date'),
        ))
