from django.views import View
from django.http import JsonResponse

from salesforce_handler.models import Lead as SFLead
from salesforce_handler.models import RaspberryPi as SFRaspberryPi
from adsrental.models.lead import Lead
from adsrental.utils import ShipStationClient
from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.utils import BotoResource


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


class SFLaunchRaspberryPiInstance(View):
    def get(self, request):
        rpid = request.GET.get('rpid')
        raspberry_pi = RaspberryPi.objects.filter(rpid=rpid).first()
        if not raspberry_pi:
            return JsonResponse({'result': False, 'reason': 'RPID not found'})

        boto_session = BotoResource()
        instance = boto_session.get_first_rpid_instance(rpid)
        if instance:
            return JsonResponse({'result': False, 'launched': False, 'exists': instance.id, 'state': instance.state['Name']})

        boto_session.launch_instance(rpid, raspberry_pi.lead.email if raspberry_pi.lead else '')
        return JsonResponse({'result': True, 'launched': True})
