from django.views import View
from django.shortcuts import redirect

from adsrental.models.lead import Lead
from adsrental.models.lead_change import LeadChange
from adsrental.forms import UserFixPasswordForm


class UserFixPasswordView(View):
    def post(self, request):
        leadid = request.session.get('leadid')
        lead = Lead.objects.filter(leadid=leadid).first()
        if not lead:
            return redirect('user_login')

        form = UserFixPasswordForm(request.POST)

        if form.is_valid():
            lead_account = form.get_lead_account(form.cleaned_data, lead)
            if lead_account:
                old_password = lead_account.password
                lead_account.password = form.cleaned_data.get('new_password')
                lead_account.wrong_password_date = None
                lead_account.save()
                LeadChange(lead=lead, lead_account=lead_account, field='wrong_password', value=lead_account.password, old_value=old_password, data='Edited by user', edited_by=None).save()

        return redirect('user_stats')
