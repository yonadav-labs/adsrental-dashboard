from django.views import View
from django.http import JsonResponse

from salesforce_handler.models import Lead as SFLead
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
            return JsonResponse({
                'result': False,
                'reason': 'No Raspberry Pi assigned',
            })

        shipstation_client = ShipStationClient()
        order = shipstation_client.add_sf_raspberry_pi_order(sf_lead)

        return JsonResponse({
            'result': True,
            'order': order.order_key,
        })
