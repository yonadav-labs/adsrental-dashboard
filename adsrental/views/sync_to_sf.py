import datetime

from django.views import View
from django.http import JsonResponse
from django.utils import timezone

from adsrental.models import Lead, RaspberryPi


class SyncToSFView(View):
    def get(self, request):
        seconds_ago = int(request.GET.get('seconds_ago', '300'))
        raspberry_pis = RaspberryPi.objects.filter(updated__gte=timezone.now() - datetime.timedelta(seconds=seconds_ago))
        if not request.GET.get('test'):
            RaspberryPi.upsert_to_sf(raspberry_pis)

        leads = Lead.objects.filter(updated__gte=timezone.now() - datetime.timedelta(seconds=seconds_ago))
        if not request.GET.get('test'):
            Lead.upsert_to_sf(leads)

        return JsonResponse({
            'result': True,
            'raspberry_pi_rpids': [i.rpid for i in raspberry_pis],
            'leads_ids': [i.leadid for i in leads],
        })
