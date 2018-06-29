from __future__ import unicode_literals

from django.views import View
from django.shortcuts import Http404
from django.http import JsonResponse

from adsrental.models.ec2_instance import EC2Instance


class EC2DataView(View):
    '''
    Get data about EC2 by RPID. Should have been used by new python RaspberryPi firmware, but was not.
    '''
    def get(self, request, rpid):
        ec2_instance = EC2Instance.get_by_rpid(rpid)
        if not ec2_instance:
            raise Http404
        if not ec2_instance.lead:
            raise Http404
        if not ec2_instance.is_active():
            raise Http404

        if not ec2_instance.is_running():
            if not ec2_instance.is_running():
                raise Http404

        return JsonResponse({
            'hostname': ec2_instance.hostname,
            'ip_address': ec2_instance.ip_address,
            'status': ec2_instance.status,
        })
