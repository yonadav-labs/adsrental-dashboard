import base64

from django.views import View
from django.shortcuts import render, redirect

from salesforce_handler.models import Lead as SFLead
from adsrental.models.lead import Lead


class ThankyouView(View):
    def get(self, request, b64_email=None):
        email = base64.b64decode(b64_email) if b64_email else None
        return render(request, 'thankyou.html', {
            'email': email,
        })

    def post(self, request, b64_email):
        email = base64.b64decode(b64_email) if b64_email else None
        if email:
            lead = Lead.objects.filter(email=email).first()
            if lead:
                lead.splashtop_id = request.POST.get('splashtop_id')
                lead.save()
            sf_lead = SFLead.objects.filter(email=email).first()
            if sf_lead:
                sf_lead.splashtop_id = request.POST.get('splashtop_id')
                sf_lead.save()
        return redirect('thankyou')
