import uuid
import base64

from django.views import View
from django.http import HttpResponse
from django.shortcuts import render, redirect

from adsrental.forms import SignupForm
from adsrental.models.lead import Lead
from adsrental.models.bundler import Bundler
from adsrental.utils import CustomerIOClient


class SignupView(View):
    def get(self, request):
        if 'utm_source' in request.GET:
            utm_source = request.GET.get('utm_source')
            request.session['utm_source'] = utm_source

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
            form_errors = []
            for error_list in form.errors.values():
                for error in error_list:
                    form_errors.append(error)
            return render(request, 'signup.html', dict(
                user=request.user,
                isp='',
                form_errors=form_errors,
                remote_addr=request.META.get('REMOTE_ADDR'),
                form=form,
            ))

        data = form.cleaned_data

        lead = Lead.objects.filter(email=data['email']).first()
        if lead:
            return redirect('thankyou_email', b64_email=base64.b64encode(lead.email))

        lead_id = str(uuid.uuid4()).replace('-', '')
        last_account_name = Lead.objects.all().order_by('-account_name').first().account_name
        account_name = 'ACT%05d' % (int(last_account_name.replace('ACT', '')) + 1)

        address = ', '.join([
            data['street'] or '',
            data['city'] or '',
            data['postal_code'] or '',
            'United States',
        ])
        lead = Lead(
            leadid=lead_id,
            account_name=account_name,
            first_name=data['first_name'],
            last_name=data['last_name'],
            status=Lead.STATUS_AVAILABLE,
            email=data['email'],
            phone=data['phone'],
            address=address,
            utm_source=data['utm_source'],
            bundler=Bundler.get_by_utm_source(data['utm_source']),
            facebook_account=True,
            facebook_account_status=Lead.STATUS_AVAILABLE,
            fb_email=base64.b64encode(data['fb_email']),
            fb_secret=base64.b64encode(data['fb_secret']),
            fb_friends=data['fb_friends'],
            fb_profile_url=data['facebook_profile_url'],
            street=data['street'],
            city=data['city'],
            state=data['state'],
            postal_code=data['postal_code'],
            country='United States',
            photo_id=data['photo_id'],
        )
        lead.save()
        lead.send_web_to_lead()

        customerio_client = CustomerIOClient()
        customerio_client.send_lead(lead)
        customerio_client.send_lead_event(lead, CustomerIOClient.EVENT_APPROVED, account_type='facebook')
        return redirect('thankyou_email', b64_email=base64.b64encode(lead.email))
