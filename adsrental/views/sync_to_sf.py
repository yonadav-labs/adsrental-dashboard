import datetime

from django.views import View
from django.http import JsonResponse
from django.utils import timezone

from adsrental.models import Lead
from salesforce_handler.models import Lead as SFLead


class SyncToSFView(View):
    def get(self, request):
        seconds_ago = int(request.GET.get('seconds_ago', '300'))
        leads = Lead.objects.filter(updated__gte=timezone.now() - datetime.timedelta(seconds=seconds_ago))[:1]
        sf_leadids = []
        leads_map = {}
        for lead in leads:
            sf_leadids.append(lead.leadid)
            leads_map[lead.leadid] = lead

        sf_leads = SFLead.objects.filter(id__in=sf_leadids).simple_select_related('raspberry_pi')
        for sf_lead in sf_leads:
            Lead.upsert_to_sf(sf_lead, leads_map.get(sf_lead.id))

        return JsonResponse({
            'result': True,
            'leads_ids': [i.leadid for i in leads],
            'seconds_ago': seconds_ago,
        })
