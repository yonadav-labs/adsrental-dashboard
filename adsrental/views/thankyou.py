from __future__ import unicode_literals

import base64

from django.views import View
from django.shortcuts import render, redirect

from adsrental.models.lead import Lead


class ThankyouView(View):
    '''
    page where use can provide his *splashtop_id*. Populates *splashtop_id* in :model:`adsrental.Lead`.
    '''
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
        return redirect('thankyou')
