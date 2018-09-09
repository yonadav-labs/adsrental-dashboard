from django.views import View
from django.http import JsonResponse

from adsrental.models.raspberry_pi import RaspberryPi


class ConnectionDataView(View):
    '''
    Get data about EC2 by RPID. Should have been used by new python RaspberryPi firmware, but was not.
    '''
    def get(self, request, rpid):
        raspberry_pi = RaspberryPi.objects.filter(rpid=rpid).first()
        if not raspberry_pi:
            return JsonResponse({
                'error': 'Not found',
                'shutdown': True,
                'result': False,
            })

        lead = raspberry_pi.get_lead()
        if not lead or not lead.is_active():
            return JsonResponse({
                'error': 'Not available',
                'shutdown': True,
                'result': False,
            })

        if not raspberry_pi.is_proxy_tunnel:
            ec2_instance = raspberry_pi.get_ec2_instance()
            return JsonResponse({
                'rpid': raspberry_pi.rpid,
                'hostname': ec2_instance.hostname if ec2_instance else '',
                'user': 'Administrator',
                'tunnel_port': 2046,
                'rtunnel_port': 3808,
                'is_proxy_tunnel': False,
                'is_beta': raspberry_pi.is_proxy_tunnel or raspberry_pi.is_beta,
                'result': True,
            })

        return JsonResponse({
            'rpid': raspberry_pi.rpid,
            'hostname': raspberry_pi.proxy_hostname,
            'user': raspberry_pi.TUNNEL_USER,
            'tunnel_port': raspberry_pi.tunnel_port,
            'rtunnel_port': raspberry_pi.rtunnel_port,
            'is_proxy_tunnel': True,
            'is_beta': raspberry_pi.is_proxy_tunnel or raspberry_pi.is_beta,
            'result': True,
        })
