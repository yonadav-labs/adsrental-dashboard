from django.views import View
from django.http import JsonResponse

from adsrental.models.bundler import Bundler
from adsrental.models.bundler_lead_stat import BundlerLeadStat


class BundlerLeadStatsCalculateView(View):
    def get(self, request):
        for bundler in Bundler.objects.all():
            BundlerLeadStat.calculate(bundler)
        return JsonResponse({
            'result': True,
        })
