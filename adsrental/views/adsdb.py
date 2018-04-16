'Views for sync from ADSDB'
import json
import uuid

from django.views import View
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.shortcuts import Http404
from django.views.decorators.csrf import csrf_exempt

from adsrental.decorators import basicauth_required
from adsrental.models.lead import Lead
from adsrental.models.lead_account import LeadAccount
from adsrental.models.lead_change import LeadChange
from adsrental.models.bundler import Bundler


@method_decorator(csrf_exempt, name='dispatch')
class ADSDBLeadView(View):
    '''
    **Update lead info from adsdb. Requires basic auth.**

    PUT https://adsrental.com/adsdb/lead/

    Parameters:

    * email - string (optional, but required if no account_id provided)
    * account_id - string (optional, but required if no email provided)
    * first_name - string (optional)
    * last_name - string (optional)
    * fb_username - string (optional)
    * fb_username - string (optional)
    * fb_password - string (optional)
    * google_username - string (optional)
    * google_password - string (optional)
    * phone - string (optional)
    * status - number (optional)

    If status = 3, lead will be banned
    '''

    @method_decorator(basicauth_required)
    def put(self, request):
        'Update lead info from ADSDB'
        if not request.user.is_staff:
            raise Http404

        try:
            data = json.loads(request.body)
        except ValueError:
            return HttpResponseBadRequest('No JSON could be decoded')

        lead_account = None
        if data.get('account_id'):
            lead_account = LeadAccount.objects.filter(adsdb_account_id=str(data.get('account_id'))).order_by('-created').first()
        if lead_account is None and data.get('email'):
            lead_account = LeadAccount.objects.filter(username=data.get('email')).order_by('-created').first()

        if not lead_account:
            raise Http404

        self._update_lead_account(lead_account, data, request.user)

        return JsonResponse(dict(result=True))

    @staticmethod
    def _update_field(lead, field_name, value, edited_by):
        old_value = getattr(lead, field_name)
        if old_value == value:
            return False

        setattr(lead, field_name, value)
        lead.save()
        LeadChange(lead=lead, old_value=old_value, value=value, edited_by=edited_by).save()
        return True

    @staticmethod
    def _update_lead_account_field(lead_account, field_name, value, edited_by):
        old_value = getattr(lead_account, field_name)
        if old_value == value:
            return False

        setattr(lead_account, field_name, value)
        lead_account.save()
        LeadChange(lead=lead_account.lead, old_value=old_value, value=value, edited_by=edited_by).save()
        return True

    @staticmethod
    def _clean_phone(value):
        if value.startswith('+1'):
            value = value[2:]

        digits = ''.join([i for i in value if i.isdigit()])
        return digits

    def _update_lead_account(self, lead_account, data, user):
        if 'first_name' in data:
            self._update_field(lead_account.lead, 'first_name', data.get('first_name'), user)
        if 'last_name' in data:
            self._update_field(lead_account.lead, 'last_name', data.get('last_name'), user)
        if 'fb_username' in data:
            self._update_lead_account_field(lead_account, 'username', data.get('fb_username'), user)
        if 'fb_password' in data:
            self._update_lead_account_field(lead_account, 'password', data.get('fb_password'), user)
        if 'google_username' in data:
            self._update_lead_account_field(lead_account, 'username', data.get('google_username'), user)
        if 'google_password' in data:
            self._update_lead_account_field(lead_account, 'password', data.get('google_password'), user)
        if 'phone' in data:
            phone = self._clean_phone(data.get('phone'))
            self._update_field(lead_account.lead, 'phone', phone, user)
        if 'status' in data:
            if data.get('status') == '3':
                lead_account.ban(user)
            else:
                lead_account.unban(user)

    def post(self, request):
        'Create lead info from ADSDB. Not used.'
        if not request.user.is_staff:
            raise Http404

        try:
            data = json.loads(request.body)
        except ValueError:
            return HttpResponseBadRequest('No JSON could be decoded')

        lead_id = str(uuid.uuid4()).replace('-', '')
        last_account_name = Lead.objects.filter(account_name__startswith='ACT').order_by('-account_name').first().account_name
        account_name = 'ACT%05d' % (int(last_account_name.replace('ACT', '')) + 1)

        bundler = Bundler.get_by_adsdb_id(data.get('bundler_id'))
        if not bundler:
            return HttpResponseBadRequest('Bundler ID not found')

        lead = Lead(
            leadid=lead_id,
            account_name=account_name,
            first_name=data['first_name'],
            last_name=data['last_name'],
            status=Lead.STATUS_AVAILABLE,
            email=data['email'],
            phone=data['phone'],
            bundler=bundler,
            utm_source=bundler.utm_source,
            street=data['street'],
            city=data['city'],
            state=data['state'],
            postal_code=data['postal_code'],
            country='United States',
        )
        lead.save()
        return JsonResponse(dict(result=True, leadid=lead_id))
