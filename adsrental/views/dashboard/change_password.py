from urllib.parse import urlencode

from django.views import View
from django.urls import reverse
from django.shortcuts import render, Http404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from adsrental.models.lead_change import LeadChange
from adsrental.models.lead_account import LeadAccount
from adsrental.forms import SetPasswordForm


class ChangePasswordView(View):
    @method_decorator(login_required)
    def get(self, request, lead_account_id):
        lead_account = LeadAccount.objects.filter(id=lead_account_id, wrong_password_date__isnull=False).first()
        if not lead_account:
            raise Http404
        form = SetPasswordForm(initial=dict(
            lead_email=lead_account.lead.email,
            email=lead_account.username,
            new_password=lead_account.password,
        ))
        return render(request, 'dashboard/change_password.html', dict(
            form=form,
            lead=lead_account.lead,
            lead_account=lead_account,
        ))

    @method_decorator(login_required)
    def post(self, request, lead_account_id):
        form = SetPasswordForm(request.POST)
        lead_account = LeadAccount.objects.filter(id=lead_account_id, wrong_password_date__isnull=False).first()
        if not lead_account:
            raise Http404

        form.lead_account = lead_account
        if form.is_valid():
            old_value = lead_account.password
            form.update_lead_account(lead_account)
            value = lead_account.password
            LeadChange(lead=lead_account.lead, lead_account=lead_account, field=LeadChange.FIELD_PASSWORD, value=value, old_value=old_value, edited_by=request.user).save()
            return HttpResponseRedirect('{}?{}'.format(
                reverse('dashboard'),
                urlencode(dict(
                    search=lead_account.lead.email,
                )),
            ))

        return render(request, 'dashboard/change_password.html', dict(
            form=form,
            lead=lead_account.lead,
            lead_account=lead_account,
        ))
