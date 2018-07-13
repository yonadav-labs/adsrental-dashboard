from __future__ import unicode_literals

from django.views import View
from django.http import JsonResponse

from adsrental.models.lead import Lead
from adsrental.utils import ShipStationClient
from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.models.ec2_instance import EC2Instance


class SFToShipstationView(View):
    'Obsolete'
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

        shipstation_client = ShipStationClient()
        if shipstation_client.get_lead_order_data(lead):
            return JsonResponse({
                'result': False,
                'reason': 'Order already exists',
            })

        order = shipstation_client.add_lead_order(lead)

        return JsonResponse({
            'result': True,
            'order': order.order_key,
        })


class SFLaunchRaspberryPiInstance(View):
    'Obsolete'
    def get(self, request):
        rpid = request.GET.get('rpid')
        lead = Lead.objects.filter(raspberry_pi__rpid=rpid).first()
        if not lead:
            return JsonResponse({'result': False, 'reason': 'RPID not found'})

        EC2Instance.launch_for_lead(lead)

        return JsonResponse({'result': True, 'launched': True})
