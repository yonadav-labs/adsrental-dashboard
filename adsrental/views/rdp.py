from django.views import View
from django.http import FileResponse, HttpResponse

from adsrental.models.ec2_instance import EC2Instance


class RDPDownloadView(View):
    def get(self, request, rpid):
        ec2_instance = EC2Instance.objects.filter(rpid=rpid).first()
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
