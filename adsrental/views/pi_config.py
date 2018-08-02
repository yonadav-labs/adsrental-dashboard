from django.views import View
from django.http import FileResponse, HttpResponseRedirect
from django.shortcuts import Http404
from django.contrib import messages

from adsrental.models.lead import Lead


class PiConfigView(View):
    'Get pi.conf file'
    def get(self, request, rpid):
        'Get pi.conf file'
        back = request.META.get('HTTP_REFERER')
        lead = Lead.objects.filter(raspberry_pi__rpid=rpid).first()
        if not lead:
            raise Http404

        if lead.is_banned():
            messages.error(request, 'RPID {} banned. Cross-check and use "Unban" if you want to get config for it.'.format(rpid))
            return HttpResponseRedirect(back)

        if not lead.is_ready_for_testing():
            messages.error(request, 'RPID {} is not ready for testing yet. Select it and use "Prepare for testing" action then download config file again.'.format(rpid))
            return HttpResponseRedirect(back)

        content = rpid
        response = FileResponse(content, content_type='application/text')
        response['Content-Disposition'] = 'attachment; filename="pi.conf"'
        return response
