from django.views import View
from django.shortcuts import redirect

from adsrental.models.lead import Lead
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
                lead_account.password = form.cleaned_data.get('new_password')
                lead_account.save()

        return redirect('user_stats')
