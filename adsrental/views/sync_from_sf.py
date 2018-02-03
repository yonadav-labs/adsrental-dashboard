import datetime

from django.views import View
from django.http import JsonResponse
from django.utils import timezone

from adsrental.models.lead import Lead
from adsrental.models.raspberry_pi import RaspberryPi
from salesforce_handler.models import Lead as SFLead
from salesforce_handler.models import RaspberryPi as SFRaspberryPi


class SyncFromSFView(View):
    def get(self, request):
        leads = []
        sf_leads = []
        sf_leads_ids = []
        seconds_ago = 15

        if request.GET.get('lead_id'):
            sf_lead_id = request.GET.get('lead_id')
            sf_lead = SFLead.objects.get(id=sf_lead_id)
            lead = Lead.objects.filter(email=sf_lead.email).first()
            Lead.upsert_from_sf(sf_lead, lead)
            return JsonResponse({
                'result': True,
                'leadid': sf_lead_id,
                'email': sf_lead.email,
            })

        if request.GET.get('raspberry_pi_id'):
            sf_raspberry_pi_id = request.GET.get('raspberry_pi_id')
            sf_raspberry_pi = SFRaspberryPi.objects.get(id=sf_raspberry_pi_id)
            rpid = sf_raspberry_pi.name
            rasberry_pi = RaspberryPi.objects.filter(rpid=rpid).first()
            RaspberryPi.upsert_from_sf(sf_raspberry_pi, rasberry_pi)
            return JsonResponse({
                'result': True,
                'rpid': rpid,
            })

        if request.GET.get('all'):
            sf_leads = SFLead.objects.all().simple_select_related('raspberry_pi')
            leads = Lead.objects.all().select_related('raspberry_pi')
        else:
            seconds_ago = int(request.GET.get('seconds_ago')) if request.GET.get('seconds_ago') else 300
            last_touch_date_min = timezone.now() - datetime.timedelta(seconds=seconds_ago)
            sf_leads = SFLead.objects.filter(last_touch_date__gt=last_touch_date_min).simple_select_related('raspberry_pi')
            sf_leads_ids = [i.id for i in sf_leads]
            leads = Lead.objects.filter(sf_leadid__in=sf_leads_ids).select_related('raspberry_pi')

        leads_map = {}
        for lead in leads:
            leads_map[lead.email] = lead

        for sf_lead in sf_leads:
            Lead.upsert_from_sf(sf_lead, leads_map.get(sf_lead.email))

        return JsonResponse({
            'result': True,
            'sf_leads_ids': sf_leads_ids,
            'sf_leads': len(sf_leads),
            'leads': len(leads),
            'seconds_ago': seconds_ago,
        })
