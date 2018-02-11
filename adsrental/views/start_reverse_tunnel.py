from __future__ import unicode_literals

from django.views import View
from django.http import JsonResponse

from adsrental.models.ec2_instance import EC2Instance


class StartReverseTunnelView(View):
    def get(self, request, rpid):
        ec2_instance = EC2Instance.obejcts.get(rpid=rpid)
        ec2_instance.ssh_execute('ssh -N -D 3808 -p 2046 pi@localhost')
        return JsonResponse(dict(result=True))
