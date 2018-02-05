from django.views import View
from django.http import JsonResponse
from django.utils import dateformat
from django.conf import settings
import requests

from adsrental.models import Lead, Bundler


class SyncToAdsdbView(View):
    def get(self, request):
        leads = Lead.objects.filter(status=Lead.STATUS_IN_PROGRESS, is_sync_adsdb=False, fb_email__isnull=False).select_related('raspberry_pi')
        saved_emails = []
        responses = []
        for lead in leads[:100]:
            bundler = lead.bundler or Bundler.get_by_utm_source(lead.utm_source)
            bundler_adsdb_id = bundler and bundler.adsdb_id
            data = dict(
                first_name=lead.first_name,
                last_name=lead.last_name,
                email=lead.email,
                fb_username=lead.fb_email,
                fb_password=lead.fb_secret,
                last_seen=dateformat.format(lead.raspberry_pi.last_seen, 'j E Y H:i') if lead.raspberry_pi and lead.raspberry_pi.last_seen else None,
                phone=lead.phone,
                ec2_hostname=lead.raspberry_pi.ec2_hostname if lead.raspberry_pi else None,
                utm_source_id=bundler_adsdb_id or settings.DEFAULT_ADSDB_BUNDLER_ID,
                rp_id=lead.raspberry_pi.rpid if lead.raspberry_pi else None,
            )
            # import json
            # raise ValueError(json.dumps(data))
            response = requests.post(
                'https://staging.adsdb.io/api/v1/accounts/create-s',
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
