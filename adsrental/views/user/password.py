from django.views import View
from django.shortcuts import redirect, get_object_or_404

from adsrental.models.lead import Lead
from adsrental.models.lead_account import LeadAccount
from adsrental.forms import UserFixPasswordForm


class UserFixPasswordView(View):
    def post(self, request, lead_account_id):
        leadid = request.session.get('leadid')
        lead = get_object_or_404(Lead, leadid=leadid)
        lead_account = get_object_or_404(LeadAccount, pk=int(lead_account_id), lead=lead)

        form = UserFixPasswordForm(request.POST)
        form.lead_account = lead_account

        if form.is_valid():
            lead_account.set_correct_password(new_password=form.cleaned_data.get('new_password'), edited_by=None)

        return redirect('user_stats')
