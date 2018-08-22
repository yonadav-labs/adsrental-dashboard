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
            raise Http404

        lead = raspberry_pi.get_lead()
        if not lead or not lead.is_active():
            raise Http404

        return JsonResponse({
            'hostname': raspberry_pi.TUNNEL_HOST,
            'user': raspberry_pi.TUNNEL_USER if raspberry_pi.is_mla else 'Administrator',
            'tunnel_host': raspberry_pi.tunnel_host or '',
            'rtunnel_host': raspberry_pi.rtunnel_host or '',
            'is_mla': raspberry_pi.is_mla,
        })
