from django.views import View
from django.http import JsonResponse

from salesforce_handler.models import Lead as SFLead
from salesforce_handler.models import RaspberryPi as SFRaspberryPi
from adsrental.models.lead import Lead
from adsrental.utils import ShipStationClient


class SFToShipstationView(View):
    def get(self, request):
        email = request.GET.get('email')
        sf_lead = SFLead.objects.filter(email=email).first()
        if not sf_lead:
            return JsonResponse({
                'result': False,
                'reason': 'Lead with given email not found',
            })

        if not sf_lead.raspberry_pi:
            sf_lead.raspberry_pi = SFRaspberryPi.objects.filter(linked_lead__isnull=True).first()
            sf_lead.raspberry_pi.linked_lead = sf_lead
            sf_lead.raspberry_pi.save()
            sf_lead.save()

        Lead.upsert_from_sf(sf_lead, Lead.objects.filter(email=email).first())

        shipstation_client = ShipStationClient()
        if shipstation_client.get_sf_lead_order_data(sf_lead):
            return JsonResponse({
                'result': False,
                'reason': 'Order already exists',
            })

        order = shipstation_client.add_sf_lead_order(sf_lead)

        return JsonResponse({
            'result': True,
            'order': order.order_key,
        })
