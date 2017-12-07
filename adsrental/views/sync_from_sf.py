from django.views import View
from django.http import JsonResponse

from adsrental.models.legacy import Lead
from salesforce_handler.models import Lead as SFLead


class SyncFromSFView(View):
    def get(self, request):
        sf_leads = SFLead.objects.all().simple_select_related('raspberry_pi')
        for sf_lead in sf_leads:
            if sf_lead.raspberry_pi and sf_lead.raspberry_pi.first_seen:
                Lead.upsert_from_sf(sf_lead)

        return JsonResponse({
            'result': True,
        })
