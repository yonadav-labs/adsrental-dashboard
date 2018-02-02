import uuid
import requests
import base64

from django.views import View
from django.http import HttpResponse
from django.shortcuts import render, redirect

from adsrental.forms import SignupForm
from adsrental.models.lead import Lead
from adsrental.utils import CustomerIOClient


class SignupView(View):
    def get(self, request):
        if 'utm_source' in request.GET:
            request.session['utm_source'] = request.GET.get('utm_source')

        utm_source = request.session.get('utm_source')
        if not utm_source:
            return HttpResponse('')

        return render(request, 'signup.html', dict(
            user=request.user,
            utm_source=request.GET.get('utm_source'),
            isp='',
            remote_addr=request.META.get('REMOTE_ADDR'),
            form=SignupForm(initial={
                'utm_source': utm_source,
            }),
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

        lead = Lead.objects.filter(email=data['email']).first()
        if lead:
            return redirect('thankyou_email', b64_email=base64.b64encode(lead.email))

        address = ', '.join([
            data['street'] or '',
            data['city'] or '',
            data['postal_code'] or '',
            'United States',
        ])
        lead = Lead(
            leadid=lead_id,
            first_name=data['first_name'],
            last_name=data['last_name'],
            status=Lead.STATUS_AVAILABLE,
            email=data['email'],
            phone=data['phone'],
            address=address,
            utm_source=data['utm_source'],
            facebook_account=True,
            facebook_account_status=Lead.STATUS_AVAILABLE,
            fb_email=base64.b64encode(data['fb_email']),
            fb_secret=base64.b64encode(data['fb_secret']),
            fb_friends=data['fb_friends'],
            fb_profile_url=data['facebook_profile_url'],
            street=data['street'],
            city=data['city'],
            postal_code=data['postal_code'],
            country='United States',
            photo_id=data['photo_id'],
        )
        lead.save()

        customerio_client = CustomerIOClient()
        customerio_client.send_lead(lead)
        customerio_client.send_lead_event(lead, CustomerIOClient.EVENT_APPROVED, account_type='facebook')
        return redirect('thankyou_email', b64_email=base64.b64encode(lead.email))
