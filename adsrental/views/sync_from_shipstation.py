import datetime

import requests
from django.views import View
from django.http import JsonResponse
from django.utils import timezone

from adsrental.models import Lead


class SyncFromShipStationView(View):
    def get(self, request):
        leads = []
        order_numbers = []
        if request.GET.get('all'):
            leads = Lead.objects.filter(pi_delivered=False, status__in=[Lead.STATUS_QUALIFIED, Lead.STATUS_AVAILABLE])
            for lead in leads:
                lead.update_from_shipstation()
        else:
            request_params = {}
            if request.GET.get('days_ago'):
                date_start = timezone.now() - datetime.timedelta(days=int(request.GET.get('days_ago')))
                request_params['shipDateStart'] = date_start.strftime('%Y-%m-%d')

            response = requests.get(
                'https://ssapi.shipstation.com/shipments',
                params=request_params,
                auth=requests.auth.HTTPBasicAuth('483e019cf2244e9484a98c913e8691b0', '4903c001173546828752c30887c9b3f9'),
            ).json()

            for row in response['shipments']:
                order_number = row['orderNumber']
                lead = Lead.objects.filter(account_name=order_number).first()
                if lead:
                    lead.update_from_shipstation(row)
                    order_numbers.append(order_number)

        return JsonResponse({
            'result': True,
            'order_numbers': order_numbers,
        })
