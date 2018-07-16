from django.views import View
from django.shortcuts import render, Http404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from adsrental.models.lead_change import LeadChange
from adsrental.models.lead import Lead
from adsrental.forms import ChangeAddressForm


class ChangeAddressView(View):
    @method_decorator(login_required)
    def get(self, request, lead_id):
        lead = Lead.objects.filter(leadid=lead_id).first()
        if not lead:
            raise Http404
        form = ChangeAddressForm(initial=dict(
            street=lead.street,
            city=lead.city,
            state=lead.state,
            postal_code=lead.postal_code,
        ))
        return render(request, 'dashboard/change_address.html', dict(
            form=form,
            lead=lead,
        ))

    @method_decorator(login_required)
    def post(self, request, lead_id):
        form = ChangeAddressForm(request.POST)
        lead = Lead.objects.get(leadid=lead_id)
        if form.is_valid():
            old_value = lead.get_address()
            form.update_lead(lead)
            value = lead.get_address()
            LeadChange(lead=lead, field='address', value=value, old_value=old_value, edited_by=request.user).save()

        return redirect('dashboard_change_address', lead_id=lead.leadid)
