from __future__ import unicode_literals

from django.views import View
from django.http import JsonResponse, HttpResponse

from adsrental.models.ec2_instance import EC2Instance


class StartReverseTunnelView(View):
    def get(self, request, rpid):
        ec2_instance = EC2Instance.objects.get(rpid=rpid)
        try:
            ec2_instance.ssh_execute('ssh -N -D 3808 -p 2046 pi@localhost')
        except:
            return JsonResponse(dict(result=False))
        return JsonResponse(dict(result=True))


class GetNetstatView(View):
    def get(self, request, rpid):
        ec2_instance = EC2Instance.objects.get(rpid=rpid.strip())
        output = ''
        try:
            output = ec2_instance.ssh_execute('netstat -an')
        except:
            pass
        return HttpResponse(output, content_type='text/plain')
