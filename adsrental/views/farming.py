from django.views import View
from django.http import FileResponse


class PiConfigView(View):
    def get(self, request, rpid):
        content = rpid
        response = FileResponse(content, content_type='application/text')
        response['Content-Disposition'] = 'attachment; filename="pi.conf"'.format(rpid)
        return response
