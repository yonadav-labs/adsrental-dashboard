from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect

from adsrental.models.lead_account_issue import LeadAccountIssue
from adsrental.forms.bundler import FixIssueForm


class FixLeadAccountIssueView(View):
    @method_decorator(login_required)
    def get(self, request, lead_account_issue_id):
        lead_account_issue = get_object_or_404(LeadAccountIssue, id=int(lead_account_issue_id))
        form = None

        if lead_account_issue.is_form_needed():
            form = FixIssueForm(initial=dict(
                old_value=lead_account_issue.get_old_value(),
                new_value=lead_account_issue.new_value or lead_account_issue.get_old_value(),
            ))

        return render(request, 'bundler/fix_lead_account_issue.html', dict(
            lead_account_issue=lead_account_issue,
            form=form,
            can_be_fixed=lead_account_issue.can_be_fixed(),
        ))

    @method_decorator(login_required)
    def post(self, request, lead_account_issue_id):
        lead_account_issue = get_object_or_404(LeadAccountIssue, id=int(lead_account_issue_id))

        if lead_account_issue.is_form_needed():
            form = FixIssueForm(request.POST)
            if not form.is_valid():
                return render(request, 'bundler/fix_lead_account_issue.html', dict(
                    lead_account_issue=lead_account_issue,
                    form=form,
                    can_be_fixed=lead_account_issue.can_be_fixed(),
                ))

        if lead_account_issue.can_be_fixed():
            lead_account_issue.submit(request.POST.get('new_value', ''), request.user)
            lead_account_issue.save()

        next_url = request.GET.get('next')
        if next_url:
            return HttpResponseRedirect(next_url)

        return redirect('bundler_fix_lead_account_issue', lead_account_issue_id=lead_account_issue_id)


class RejectLeadAccountIssueView(View):
    @method_decorator(login_required)
    def get(self, request, lead_account_issue_id):
        lead_account_issue = get_object_or_404(LeadAccountIssue, id=int(lead_account_issue_id))
        if lead_account_issue.can_be_resolved():
            lead_account_issue.reject(request.user)
            lead_account_issue.save()

        next_url = request.GET.get('next')
        if next_url:
            return HttpResponseRedirect(next_url)

        return redirect('bundler_fix_lead_account_issue', lead_account_issue_id=lead_account_issue_id)
