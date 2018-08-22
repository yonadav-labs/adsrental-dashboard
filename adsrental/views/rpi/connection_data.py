from django.views import View
from django.shortcuts import Http404
from django.http import JsonResponse

from adsrental.models.raspberry_pi import RaspberryPi


class ConnectionDataView(View):
    '''
    Get data about EC2 by RPID. Should have been used by new python RaspberryPi firmware, but was not.
    '''
    def get(self, request, rpid):
        raspberry_pi = RaspberryPi.objects.filter(rpid=rpid).first()
        if not raspberry_pi:
            return JsonResponse({'error': 'Not found'})

        lead = raspberry_pi.get_lead()
        if not lead or not lead.is_active():
            return JsonResponse({'error': 'Not available'})

        return JsonResponse({
            'hostname': raspberry_pi.TUNNEL_HOST,
            'user': raspberry_pi.TUNNEL_USER if raspberry_pi.is_mla else 'Administrator',
            'tunnel_port': raspberry_pi.tunnel_port or '',
            'rtunnel_port': raspberry_pi.rtunnel_port or '',
            'is_mla': raspberry_pi.is_mla,
        })
