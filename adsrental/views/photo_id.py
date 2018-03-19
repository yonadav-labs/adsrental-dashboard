from __future__ import unicode_literals

from django.views import View
from django.shortcuts import Http404
from django.http import HttpResponse

from adsrental.models.lead import Lead


class PhotoIdView(View):
    def get(self, request, leadid):
        lead = Lead.objects.filter(leadid=leadid).first()
        if not lead or not lead.photo_id:
            raise Http404

        filename = lead.photo_id.name.split('/')[-1]
        response = HttpResponse(lead.photo_id, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response
