from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.http import FileResponse
from django.shortcuts import Http404

from adsrental.models.raspberry_pi import RaspberryPi


class EC2RDPFileView(View):
    @method_decorator(login_required)
    def get(self, request, rpid):
        raspberry_pi = RaspberryPi.objects.filter(rpid=rpid).first()
        ec2_instance = raspberry_pi.get_ec2_instance()

        if not ec2_instance:
            raise Http404

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
