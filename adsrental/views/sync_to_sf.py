import datetime

from django.views import View
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q

from adsrental.models import Lead
from salesforce_handler.models import Lead as SFLead


class SyncToSFView(View):
    def get(self, request):
        seconds_ago = int(request.GET.get('seconds_ago', '300'))
        all = request.GET.get('all')
        if all:
            leads = Lead.objects.all().select_related('raspberry_pi')
        else:
            leads = Lead.objects.filter(
                Q(updated__gte=timezone.now() - datetime.timedelta(seconds=seconds_ago)) |
                Q(raspberry_pi__updated__gte=timezone.now() - datetime.timedelta(seconds=seconds_ago))
            ).select_related('raspberry_pi')
        sf_leadids = []
        errors = []
        leads_map = {}
        for lead in leads:
            sf_leadids.append(lead.leadid)
            leads_map[lead.leadid] = lead

        if all:
            sf_leads = SFLead.objects.all().simple_select_related('raspberry_pi')
        else:
            sf_leads = SFLead.objects.all().simple_select_related('raspberry_pi')
            sf_leads = [i for i in sf_leads if i.id in sf_leadids]
        for sf_lead in sf_leads:
            try:
                Lead.upsert_to_sf(sf_lead, leads_map.get(sf_lead.id))
            except Exception as e:
                errors.append([sf_lead.id, str(e)])

        return JsonResponse({
            'all': all,
            'result': True,
            'leads_ids': [i.leadid for i in leads],
            'sfleads_ids': [i.id for i in sf_leads],
            'seconds_ago': seconds_ago,
            'errors': errors,
        })
