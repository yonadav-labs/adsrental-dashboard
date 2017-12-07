import datetime

from django.views import View
from django.http import JsonResponse
from django.utils import timezone

from adsrental.models.legacy import Lead, RaspberryPi


class SyncToSFView(View):
    def get(self, request):
        seconds_ago = int(request.GET.get('seconds_ago', '300'))
        raspberry_pis = RaspberryPi.objects.filter(updated__gte=timezone.now() - datetime.timedelta(seconds=seconds_ago))
        RaspberryPi.upsert_to_sf(raspberry_pis)

        leads = Lead.objects.filter(updated__gte=timezone.now() - datetime.timedelta(seconds=seconds_ago))
        Lead.upsert_to_sf(leads)

        return JsonResponse({
            'result': True,
        })
