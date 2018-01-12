import uuid
import requests
import base64
import time

from django.views import View
from django.http import HttpResponseRedirect
from django.shortcuts import render

from adsrental.forms import SignupForm
from adsrental.models.lead import Lead
from salesforce_handler.models import Lead as SFLead


class SignupView(View):
    def get(self, request):
        return render(request, 'signup.html', dict(
            user=request.user,
            isp='',
            remote_addr=request.META.get('REMOTE_ADDR'),
            form=SignupForm(),
        ))

    def post(self, request):
        form = SignupForm(request.POST, request.FILES)
        if not form.is_valid():
            # raise ValueError(form.errors)
            return render(request, 'signup.html', dict(
                user=request.user,
                isp='',
                remote_addr=request.META.get('REMOTE_ADDR'),
                form=form,
            ))

        data = form.cleaned_data
        # raise ValueError(data)
        lead_id = str(uuid.uuid4()).replace('-', '')

        response = requests.post(
            'https://webto.salesforce.com/servlet/servlet.WebToLead?encoding=UTF-8',
            data={
                'oid': '00D460000015t1L',
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'company': '[Empty]',
                'city': data['city'],
                'state': data['state'],
                'phone': data['phone'],
                'street': data['street'],
                'country': 'United States',
                'zip': data['postal_code'],
                '00N4600000AuUxk': lead_id,
                'debug': 1,
                'debugEmail': 'volshebnyi@gmail.com',
                '00N46000009vg39': request.META.get('REMOTE_ADDR'),
                '00N46000009vg3J': 'ISP',
                '00N46000009wgvp': data['facebook_profile_url'],
                '00N46000009whHW': data['utm_source'],
                '00N46000009whHb': request.META.get('HTTP_USER_AGENT'),
                '00N4600000B0zip': 1,
                '00N4600000B1Sup': 'Available',
                'Facebook_Email__c': base64.b64encode(data['fb_email']),
                'Facebook_Password__c': base64.b64encode(data['fb_secret']),
                'Facebook_Friends__c': data['fb_friends'],
                'email': data['email'],
                'Photo_Id_Url__c': 'https://adsrental.com/app/photo/{}/'.format(base64.b64encode(data['email'])),
            }
        )
        if response.status_code != 200:
            return render(request, 'signup.html', dict(
                user=request.user,
                isp='',
                remote_addr=request.META.get('REMOTE_ADDR'),
                form=form,
            ))

        sf_lead = None
        attempts = 0
        while not sf_lead and attempts < 10:
            sf_lead = SFLead.objects.filter(email=data['email']).first()
            time.sleep(1)
            attempts = attempts + 1

        if attempts == 10:
            return HttpResponseRedirect('/thankyou.php?email={}'.format(data['email']))

        lead = Lead.objects.filter(email=data['email']).first()
        lead = Lead.upsert_from_sf(sf_lead, lead)
        lead.photo_id = data['photo_id']
        lead.save()
        # return render(request, 'signup.html', dict(
        #     user=request.user,
        #     uid=str(uuid.uuid4()),
        #     isp='',
        #     remote_addr=request.META.get('REMOTE_ADDR'),
        # ))

        lead.send_customer_io_event('lead_approved', account_type='facebook')
        return HttpResponseRedirect('/thankyou.php?email={}'.format(data['email']))
