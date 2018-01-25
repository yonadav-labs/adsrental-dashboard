from django.views import View
from django.http import JsonResponse

from salesforce_handler.models import Lead as SFLead
from adsrental.models.lead import Lead
from adsrental.utils import ShipStationClient
from salesforce_handler.models import RaspberryPi as SFRaspberryPi
from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.models.ec2_instance import EC2Instance


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
            lead.raspberry_pi = RaspberryPi.objects.filter(lead__isnull=True, rpid__startswith='RP').first()
            lead.save()

        sf_raspberry_pi = SFRaspberryPi.objects.filter(name=lead.raspberry_pi.rpid).first()
        RaspberryPi.upsert_to_sf(sf_raspberry_pi, lead.raspberry_pi)
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
        EC2Instance.launch_for_lead(lead)

        return JsonResponse({
            'result': True,
            'order': order.order_key,
        })


class SFLaunchRaspberryPiInstance(View):
    def get(self, request):
        rpid = request.GET.get('rpid')
        lead = Lead.objects.filter(raspberry_pi__rpid=rpid).first()
        if not lead:
            return JsonResponse({'result': False, 'reason': 'RPID not found'})

        EC2Instance.launch_for_lead(lead)

        return JsonResponse({'result': True, 'launched': True})
