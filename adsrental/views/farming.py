from __future__ import unicode_literals

from django.views import View
from django.http import FileResponse, HttpResponseRedirect
from django.shortcuts import Http404
from django.contrib import messages

from adsrental.models.lead import Lead


class PiConfigView(View):
    def get(self, request, rpid):
        back = request.META.get('HTTP_REFERER')
        lead = Lead.objects.filter(raspberry_pi__rpid=rpid).first()
        if not lead:
            raise Http404

        if not lead.is_ready_for_testing():
            messages.error(request, 'RPID {} is not ready for testing yet. Select it and use "Prepare for testing" action then download config file again.'.format(rpid))
            return HttpResponseRedirect(back)

        content = rpid
        response = FileResponse(content, content_type='application/text')
        response['Content-Disposition'] = 'attachment; filename="pi.conf"'.format(rpid)
        return response
