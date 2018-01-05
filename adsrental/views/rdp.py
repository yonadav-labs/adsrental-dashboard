from django.views import View
from django.http import FileResponse, Http404

from adsrental.models.lead import Lead


class RDPDownloadView(View):
    def get(self, request, rpid):
        lead = Lead.objects.filter(raspberry_pi__rpid=rpid).first()
        if not lead:
            raise Http404()

        lines = []
        lines.append('auto connect:i:1')
        lines.append('full address:s:{}:23255'.format(lead.raspberry_pi.ec2_hostname))
        lines.append('username:s:Administrator')
        lines.append('password:s:Dk.YDq8pXQS-R5ZAn84Lgma9rFvGlfvL')
        lines.append('')
        content = '\n'.join(lines)

        response = FileResponse(content, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="{}.rdp"'.format(rpid)
        return response
