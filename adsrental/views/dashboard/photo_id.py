import mimetypes

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

        mimetype = mimetypes.guess_type(filename)[0] or 'text/plain'
        try:
            response = HttpResponse(lead.photo_id, content_type=mimetype)
        except FileNotFoundError:
            raise Http404
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response
