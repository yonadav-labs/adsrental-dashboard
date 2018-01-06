from django.views import View
from django.http import JsonResponse

from adsrental.models import Lead


class SyncDeliveredView(View):
    def get(self, request):
        leads = []
        delivered = []
        not_delivered = []
        all = request.GET.get('all')
        if all:
            leads = Lead.objects.filter(usps_tracking_code__isnull=False)
        else:
            leads = Lead.objects.filter(usps_tracking_code__isnull=False, pi_delivered=False)
        for lead in leads:
            lead.update_pi_delivered()
            if lead.pi_delivered:
                delivered.append(lead.leadid)
            else:
                not_delivered.append(lead.leadid)

        return JsonResponse({
            'all': all,
            'result': True,
            'delivered': delivered,
            'not_delivered': not_delivered,
        })
