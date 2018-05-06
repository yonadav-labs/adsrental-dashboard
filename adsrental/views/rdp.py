from __future__ import unicode_literals

from django.views import View
from django.http import FileResponse, HttpResponse
from django.shortcuts import render

from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.models.ec2_instance import EC2Instance


class RDPDownloadView(View):
    def get(self, request, rpid):
        raspberry_pi = RaspberryPi.objects.filter(rpid=rpid).first()
        ec2_instance = raspberry_pi.get_ec2_instance()

        if not ec2_instance:
            return HttpResponse('EC2 instance {} does not exist'.format(rpid))

        lines = []
        lines.append('auto connect:i:1')
        lines.append('full address:s:{}:23255'.format(ec2_instance.hostname))
        lines.append('username:s:Administrator')
        lines.append('password:s:{}'.format(ec2_instance.password))
        lines.append('')
        content = '\n'.join(lines)

        response = FileResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="{}.rdp"'.format(rpid)
        return response


class RDPConnectView(View):
    def get(self, request):
        rpid = request.GET.get('rpid', '')
        ec2_instance = EC2Instance.objects.filter(rpid=rpid).first()
        ec2_instance.update_from_boto()
        if not ec2_instance.is_stopped():
            ec2_instance.start()

        return render(request, 'rdp_connect.html', dict(
            rpid=rpid,
            ec2_instance=ec2_instance,
        ))
