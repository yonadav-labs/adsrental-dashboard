from django.views import View
from django.http import JsonResponse

from salesforce_handler.models import Lead as SFLead
from adsrental.models.lead import Lead
from adsrental.utils import ShipStationClient
from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.utils import BotoResource


class SFToShipstationView(View):
    def get(self, request):
        email = request.GET.get('email')
        lead = Lead.objects.filter(email=email).first()
        if not lead:
            return JsonResponse({
                'result': False,
                'reason': 'Lead with given email not found',
            })

        if not lead.raspberry_pi:
            lead.raspberry_pi = RaspberryPi.objects.filter(lead__isnull=True).first()
            lead.raspberry_pi.save()
            lead.save()

        sf_lead = SFLead.objects.filter(email=email).first()
        Lead.upsert_to_sf(sf_lead, lead)
        sf_lead = SFLead.objects.filter(email=email).first()

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
            instance_state = instance.state['Name']
            started = False
            if instance_state == 'stopped':
                instance.start()
                started = True
            return JsonResponse({'result': False, 'launched': False, 'exists': instance.id, 'state': instance.state['Name'], 'started': started})

        boto_session.launch_instance(rpid, raspberry_pi.lead.email if raspberry_pi.lead else '')
        return JsonResponse({'result': True, 'launched': True})
