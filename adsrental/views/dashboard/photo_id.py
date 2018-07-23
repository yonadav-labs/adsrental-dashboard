from django.views import View
from django.http import HttpResponse
from django.shortcuts import Http404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from adsrental.models.lead import Lead


class PhotoIDVIew(View):
    @method_decorator(login_required)
    def get(self, request, lead_id):
        lead = Lead.objects.filter(leadid=lead_id).first()
        if not lead or not lead.photo_id:
            raise Http404

        filename = lead.photo_id.name.split('/')[-1]
        response = HttpResponse(lead.photo_id, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response
