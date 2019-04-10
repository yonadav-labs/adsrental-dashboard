from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect

from adsrental.models.lead_account import LeadAccount
from adsrental.models.lead_account_issue import LeadAccountIssue
from adsrental.forms.bundler import FixIssueForm, ReportIssueForm


class ReportLeadAccountIssueView(View):
    @method_decorator(login_required)
    def get(self, request, lead_account_id):
        lead_account = get_object_or_404(LeadAccount, id=int(lead_account_id))
        form = ReportIssueForm()

        return render(request, 'bundler/report_lead_account_issue.html', dict(
            lead_account=lead_account,
            form=form,
        ))

    @method_decorator(login_required)
    def post(self, request, lead_account_id):
        lead_account = get_object_or_404(LeadAccount, id=int(lead_account_id))
        form = ReportIssueForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, 'bundler/report_lead_account_issue.html', dict(
                lead_account=lead_account,
                form=form,
            ))

        issue = LeadAccountIssue(
            lead_account=lead_account,
            issue_type=form.cleaned_data['issue_type'],
        )
        issue.insert_note(f'Reported by {request.user}')
        if form.cleaned_data['note']:
            issue.insert_note(form.cleaned_data['note'])
        if form.cleaned_data['image']:
            issue.image = form.cleaned_data['image']
        issue.save()
        messages.success(request, 'New issue reported')

        next_url = request.GET.get('next')
        if next_url:
            return HttpResponseRedirect(next_url)

        return redirect('bundler_issues_dashboard', lead_account_id=lead_account.id)


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
            form.lead_account_issue = lead_account_issue
            if not form.is_valid():
                return render(request, 'bundler/fix_lead_account_issue.html', dict(
                    lead_account_issue=lead_account_issue,
                    form=form,
                    can_be_fixed=lead_account_issue.can_be_fixed(),
                ))

        if lead_account_issue.can_be_fixed():
            lead_account_issue.submit(request.POST.get('new_value', ''), request.user)
            lead_account_issue.save()

        messages.success(request, 'Fix submitted')

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

        messages.success(request, 'Fix rejected')
        next_url = request.GET.get('next')
        if next_url:
            return HttpResponseRedirect(next_url)

        return redirect('bundler_fix_lead_account_issue', lead_account_issue_id=lead_account_issue_id)
