from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from adsrental.models.lead import Lead
from adsrental.models.lead_account_issue import LeadAccountIssue
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

        lead_accounts = lead.lead_accounts.all()
        issues = LeadAccountIssue.objects.filter(lead_account__in=lead_accounts, status__in=[
            LeadAccountIssue.STATUS_REPORTED,
            LeadAccountIssue.STATUS_REJECTED,
        ], issue_type__in=[
            LeadAccountIssue.ISSUE_TYPE_WRONG_PASSWORD,
        ])

        return render(request, 'user/stats.html', dict(
            lead=lead,
            lead_accounts=lead_accounts,
            issues=issues,
            raspberry_pi=lead.raspberry_pi,
            lead_histories_month=LeadHistoryMonth.objects.filter(lead=lead).order_by('-date'),
        ))


class AdminUserStatsView(View):
    @method_decorator(login_required)
    def get(self, request, rpid):
        if not request.user.is_superuser:
            return redirect('login')

        lead = Lead.objects.filter(raspberry_pi__rpid=rpid).first()
        if not lead:
            return redirect('login')

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
