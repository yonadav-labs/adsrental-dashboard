from django.views import View
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import FileResponse

from adsrental.models.vultr_instance import VultrInstance


class VultrRDPFileView(View):
    @method_decorator(login_required)
    def get(self, request, vultr_instance_id):
        vultr_instance = get_object_or_404(VultrInstance, id=vultr_instance_id)

        lines = []
        lines.append('auto connect:i:1')
        lines.append('full address:s:{}:{}'.format(vultr_instance.ip_address, vultr_instance.RDP_PORT))
        lines.append('username:s:{}'.format(vultr_instance.USERNAME))
        lines.append('password:s:{}'.format(vultr_instance.password))
        lines.append('')
        content = '\n'.join(lines)

        response = FileResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="{}.rdp"'.format(vultr_instance.instance_id)
        return response
