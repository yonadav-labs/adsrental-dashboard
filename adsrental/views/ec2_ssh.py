from __future__ import unicode_literals

from django.views import View
from django.shortcuts import Http404
from django.http import JsonResponse, HttpResponse

from adsrental.models.ec2_instance import EC2Instance


class StartReverseTunnelView(View):
    def get(self, request, rpid):
        ec2_instance = EC2Instance.objects.filter(rpid=rpid.strip()).first()
        if not ec2_instance:
            raise Http404
        try:
            ec2_instance.ssh_execute('ssh -N -D 3808 -p 2046 pi@localhost')
        except Exception:
            return JsonResponse(dict(result=False))
        return JsonResponse(dict(result=True))


class GetNetstatView(View):
    def get(self, request, rpid):
        ec2_instance = EC2Instance.objects.filter(rpid=rpid.strip()).first()
        if not ec2_instance:
            raise Http404
        output = ''
        try:
            output = ec2_instance.ssh_execute('netstat -an')
        except Exception:
            pass
        return HttpResponse(output, content_type='text/plain')
