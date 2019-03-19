from django.views import View
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, get_object_or_404, redirect

from adsrental.admin.lead_admin import LeadAdmin
from adsrental.admin.lead_account_admin import LeadAccountAdmin
from adsrental.admin.lead_history_admin import LeadHistoryAdmin
from adsrental.admin.lead_account_issue_admin import LeadAccountIssueAdmin
from adsrental.models.lead_account_issue import LeadAccountIssue


class AdminActionView(View):
    admin_models = {
        'LeadAdmin': LeadAdmin,
        'LeadAccountAdmin': LeadAccountAdmin,
        'LeadHistoryAdmin': LeadHistoryAdmin,
        'LeadAccountIssueAdmin': LeadAccountIssueAdmin,
    }

    @method_decorator(login_required)
    def get(self, request, model_name, action_name, object_id):
        admin_model_cls = self.admin_models[model_name]
        queryset = admin_model_cls.model.objects.filter(pk=object_id)

        result = getattr(admin_model_cls, action_name)(admin_model_cls, request, queryset)
        if result:
            return result

        next_url = request.GET.get('next')
        if next_url:
            return HttpResponseRedirect(next_url)

        return redirect('admin:index')

    @method_decorator(login_required)
    def post(self, request, model_name, action_name, object_id):
        next_url = request.GET.get('next')
        admin_model_cls = self.admin_models[model_name]
        queryset = admin_model_cls.model.objects.filter(pk=object_id)

        result = getattr(admin_model_cls, action_name)(admin_model_cls, request, queryset)
        if result:
            return result

        return HttpResponseRedirect(next_url)


class ResolveLeadAccountIssueView(View):
    @method_decorator(login_required)
    def get(self, request, lead_account_issue_id):
        if not request.user.is_superuser:
            raise Http404

        lead_account_issue = get_object_or_404(LeadAccountIssue, id=int(lead_account_issue_id))

        return render(request, 'admin/resolve_lead_account_issue.html', dict(
            lead_account_issue=lead_account_issue,
        ))

    @method_decorator(login_required)
    def post(self, request, lead_account_issue_id):
        if not request.user.is_superuser:
            raise Http404

        lead_account_issue = get_object_or_404(LeadAccountIssue, id=int(lead_account_issue_id))
        if lead_account_issue.can_be_resolved():
            lead_account_issue.resolve(request.user)
            lead_account_issue.save()

        next_url = request.GET.get('next')
        if next_url:
            return HttpResponseRedirect(next_url)

        return redirect('admin_helpers:resolve_lead_account_issue', lead_account_issue_id=lead_account_issue_id)
