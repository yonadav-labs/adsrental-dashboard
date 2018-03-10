from __future__ import unicode_literals

import json

from django.views import View
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.shortcuts import Http404
from adsrental.decorators import basicauth_required
from django.views.decorators.csrf import csrf_exempt


from adsrental.models.lead import Lead
from adsrental.models.lead_change import LeadChange


@method_decorator(csrf_exempt, name='dispatch')
class ADSDBUpdateLead(View):
    '''
    Update lead info from adsdb. Requires basic auth.

    POST https://adsrental.com/adsdb/update_lead/

    Parameters:

    * email - string (required)
    * first_name - string (optional)
    * last_name - string (optional)
    * fb_username - string (optional)
    * fb_password - string (optional)
    * google_username - string (optional)
    * google_password - string (optional)
    * phone - string (optional)
    * status - number (optional)

    If status = 4, lead will be banned
    '''
    @method_decorator(basicauth_required)
    def get(self, request):
        if not request.user.is_staff:
            raise Http404

        data = request.GET
        lead = Lead.objects.filter(email=data.get('email')).first()
        if not lead:
            raise Http404

        self.update_lead(lead, data, request.user)

        return JsonResponse(dict(result=True))

    @method_decorator(basicauth_required)
    def put(self, request):
        if not request.user.is_staff:
            raise ValueError(request.META)
            raise Http404

        try:
            data = json.loads(request.body)
        except:
            return HttpResponseBadRequest('No JSON could be decoded')

        lead = Lead.objects.filter(email=data.get('email')).first()
        if not lead:
            raise Http404

        self.update_lead(lead, data, request.user)

        return JsonResponse(dict(result=True))

    def update_field(self, lead, field_name, value, edited_by):
        old_value = getattr(lead, field_name)
        if old_value == value:
            return False

        setattr(lead, field_name, value)
        lead.save()
        LeadChange(lead=lead, old_value=old_value, new_value=value, edited_by=edited_by).save()

    def update_lead(self, lead, data, user):
        if 'first_name' in data:
            self.update_field(lead, 'first_name', data.get('first_name'), user)
        if 'last_name' in data:
            self.update_field(lead, 'last_name', data.get('last_name'), user)
        if 'fb_username' in data:
            self.update_field(lead, 'fb_email', data.get('fb_username'), user)
        if 'fb_password' in data:
            self.update_field(lead, 'fb_secret', data.get('fb_password'), user)
        if 'google_username' in data:
            self.update_field(lead, 'google_email', data.get('google_username'), user)
        if 'google_password' in data:
            self.update_field(lead, 'google_password', data.get('google_password'), user)
        if 'phone' in data:
            self.update_field(lead, 'phone', data.get('phone'), user)
