import datetime

from django.views import View
from django.http import JsonResponse
from django.utils import timezone

from adsrental.models import Lead
from salesforce_handler.models import Lead as SFLead


class SyncFromSFView(View):
    def get(self, request):
        minutes_ago = int(request.GET.get('minutes')) if request.GET.get('minutes') else 15
        last_touch_date_min = timezone.now() - datetime.timedelta(minutes=minutes_ago)
        sf_leads = SFLead.objects.filter(last_touch_date__gt=last_touch_date_min).simple_select_related('raspberry_pi')
        sf_leads_ids = [i.id for i in sf_leads]
        if request.GET.get('all'):
            leads = Lead.objects.all().select_related('raspberry_pi')
            
        else:
            leads = Lead.objects.filter(leadid__in=sf_leads_ids).select_related('raspberry_pi')

        leads_map = {}
        for lead in leads:
            leads_map[lead.leadid] = lead

        for sf_lead in sf_leads:
            Lead.upsert_from_sf(sf_lead, leads_map.get(sf_lead.id))

        return JsonResponse({
            'result': True,
            'sf_leads_ids': sf_leads_ids,
            'sf_leads': len(sf_leads),
            'leads': len(leads),
        })
