
import base64

from django.views import View
from django.shortcuts import render, redirect

from salesforce_handler.models import Lead as SFLead


class ThankyouView(View):
    def get(self, request, b64_email=None):
        return render(request, 'thankyou.html')

    def post(self, request, b64_email=None):
        email = base64.b64decode(b64_email)
        sf_lead = SFLead.objects.filter(email=email).first()
        sf_lead.splashtop_id = request.POST.get('splashtop_id')
        sf_lead.save()
        return redirect('thankyou')
