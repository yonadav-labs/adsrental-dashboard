from django.views import View
from django.shortcuts import render, Http404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.http import HttpResponseRedirect

from adsrental.models.lead_account import LeadAccount
from adsrental.forms import DisqualifyLeadAccountForm


class DisqualifyLeadAccountView(View):
    @method_decorator(login_required)
    def get(self, request, lead_account_id):
        next_url = request.GET.get('next')
        lead_account = LeadAccount.objects.filter(id=lead_account_id).first()
        if not lead_account or lead_account.status != LeadAccount.STATUS_AVAILABLE:
            raise Http404
        form = DisqualifyLeadAccountForm(initial=dict(
            lead_account_id=lead_account_id,
            next=next_url,
        ))
        return render(request, 'dashboard/disqualify_lead_account.html', dict(
            form=form,
            lead_account=lead_account,
        ))

    @method_decorator(login_required)
    def post(self, request, lead_account_id):
        lead_account = LeadAccount.objects.filter(id=lead_account_id).first()
        if not lead_account or lead_account.status != LeadAccount.STATUS_AVAILABLE:
            raise Http404

        form = DisqualifyLeadAccountForm(request.POST)
        if form.is_valid():
            lead_account.disqualify(request.user)
            messages.success(request, 'Lead account {} is disqualified now'.format(lead_account.username))

        return HttpResponseRedirect(form.cleaned_data.get('next', ''))
