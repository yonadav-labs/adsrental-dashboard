from django.views import View
from django.shortcuts import redirect, get_object_or_404, render
from django.http import HttpResponseRedirect

from adsrental.models.lead import Lead
from adsrental.models.lead_account_issue import LeadAccountIssue
from adsrental.forms.bundler import FixIssueForm, FixIssueNoValueForm


class FixLeadAccountIssueView(View):
    def get(self, request, lead_account_issue_id):
        leadid = request.session.get('leadid')
        lead = get_object_or_404(Lead, leadid=leadid)
        lead_account_issue = get_object_or_404(LeadAccountIssue, id=int(lead_account_issue_id), lead_account__lead=lead)
        form = None

        if lead_account_issue.is_value_needed():
            form = FixIssueForm(initial=dict(
                old_value=lead_account_issue.get_old_value(),
                new_value=lead_account_issue.new_value or lead_account_issue.get_old_value(),
            ))
        else:
            form = FixIssueNoValueForm()

        return render(request, 'user/fix_lead_account_issue.html', dict(
            lead_account_issue=lead_account_issue,
            form=form,
        ))

    def post(self, request, lead_account_issue_id):
        leadid = request.session.get('leadid')
        lead = get_object_or_404(Lead, leadid=leadid)
        lead_account_issue = get_object_or_404(LeadAccountIssue, id=int(lead_account_issue_id), lead_account__lead=lead)

        if lead_account_issue.is_value_needed():
            form = FixIssueForm(request.POST)
        else:
            form = FixIssueNoValueForm(request.POST)

        form.lead_account_issue = lead_account_issue
        form.user = request.user
        if not form.is_valid():
            return render(request, 'user/fix_lead_account_issue.html', dict(
                lead_account_issue=lead_account_issue,
                form=form,
            ))

        if lead_account_issue.can_be_fixed():
            lead_account_issue.submit(form.cleaned_data.get('new_value', ''), 'user')
            if form.cleaned_data.get('note'):
                lead_account_issue.insert_note(f"Fix note: {form.cleaned_data['note']}")
            if form.cleaned_data.get('image'):
                lead_account_issue.image = form.cleaned_data['image']
            lead_account_issue.save()

        next_url = request.GET.get('next')
        if next_url:
            return HttpResponseRedirect(next_url)

        return redirect('user_fix_lead_account_issue', lead_account_issue_id=lead_account_issue_id)
