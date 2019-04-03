from django.shortcuts import render, Http404, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from adsrental.models.bundler import Bundler
from adsrental.models.lead_account import LeadAccount
from adsrental.models.lead_account_issue import LeadAccountIssue
from adsrental.forms.bundler import BundlerIssuesForm


class IssuesDashboardView(View):
    @method_decorator(login_required)
    def get(self, request, lead_account_id=None):
        bundlers = []
        if request.user.is_superuser:
            bundlers = Bundler.objects.all()

        if request.user.bundler:
            bundlers = [request.user.bundler]

        if not bundlers:
            raise Http404

        lead_account = None
        issues = LeadAccountIssue.objects.filter(
            lead_account__lead__bundler__in=bundlers,
            status__in=[
                LeadAccountIssue.STATUS_REPORTED,
                LeadAccountIssue.STATUS_REJECTED,
                LeadAccountIssue.STATUS_SUBMITTED,
            ]
        )

        if lead_account_id is not None:
            lead_account = get_object_or_404(LeadAccount, id=int(lead_account_id))
            issues = issues.filter(lead_account=lead_account)

        issues = issues.select_related('lead_account', 'lead_account__lead', 'lead_account__lead__bundler')

        form = BundlerIssuesForm(request.GET)
        if form.is_valid():
            issues = form.filter(issues)

        return render(request, 'bundler/issues_dashboard.html', dict(
            form=form,
            bundlers=bundlers,
            lead_account=lead_account,
            issues=issues
        ))
