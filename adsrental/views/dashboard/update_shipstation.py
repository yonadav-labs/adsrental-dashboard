from django.views import View
from django.shortcuts import Http404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class UpdateShipstationView(View):
    @method_decorator(login_required)
    def get(self, request, lead_id):
        raise Http404
