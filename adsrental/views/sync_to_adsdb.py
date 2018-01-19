from django.views import View
from django.http import JsonResponse
from django.utils import dateformat
import requests

from adsrental.models import Lead


class SyncToAdsdbView(View):
    def get(self, request):
        leads = Lead.objects.filter(status=Lead.STATUS_IN_PROGRESS, is_sync_adsdb=False, fb_email__isnull=False).select_related('raspberry_pi')
        saved_emails = []
        responses = []
        for lead in leads[:10]:
            data = dict(
                first_name=lead.first_name,
                last_name=lead.last_name,
                email=lead.email,
                fb_username=lead.fb_email,
                fb_password=lead.fb_secret,
                last_seen=dateformat.format(lead.raspberry_pi.last_seen, 'j E Y H:i') if lead.raspberry_pi and lead.raspberry_pi.last_seen else None,
                phone=lead.phone,
                ec2_hostname=lead.raspberry_pi.ec2_hostname if lead.raspberry_pi else None,
                utm_source_id=20,
            )
            # import json
            # raise ValueError(json.dumps(data))
            response = requests.post(
                'https://www.adsdb.io/api/v1/accounts/create-s',
                json=[data],
                auth=requests.auth.HTTPBasicAuth('timothy@adsinc.io', 'timgoat900'),
            )
            if response.status_code != 200:
                raise ValueError(response.status_code, response.content)

            responses.append(response.content)

            lead.is_sync_adsdb = True
            lead.save()
            saved_emails.append(lead.email)

            # print lead

        return JsonResponse({
            'result': True,
            'saved_emails': saved_emails,
            'responses': responses,
        })
