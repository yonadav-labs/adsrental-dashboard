from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect

from adsrental.models.lead_account_issue import LeadAccountIssue


class FixLeadAccountIssueView(View):
    @method_decorator(login_required)
    def get(self, request, lead_account_issue_id):
        lead_account_issue = get_object_or_404(LeadAccountIssue, id=int(lead_account_issue_id))

        return render(request, 'bundler/fix_lead_account_issue.html', dict(
            lead_account_issue=lead_account_issue,
            can_be_fixed=lead_account_issue.can_be_fixed(),
        ))

    @method_decorator(login_required)
    def post(self, request, lead_account_issue_id):
        lead_account_issue = get_object_or_404(LeadAccountIssue, id=int(lead_account_issue_id))
        next_url = request.GET.get('next')
        if lead_account_issue.can_be_fixed():
            lead_account_issue.submit('test', request.user)
            lead_account_issue.save()

        if next_url:
            return HttpResponseRedirect(next_url)

        return redirect('bundler_fix_lead_account_issue')
