import datetime

import requests
from django.views import View
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings

from adsrental.models import Lead


class SyncFromShipStationView(View):
    def get(self, request):
        order_numbers = []
        orders_new = []
        orders_not_found = []
        days_ago = int(request.GET.get('days_ago', '1'))
        force = request.GET.get('force')
        request_params = {}
        date_start = timezone.now() - datetime.timedelta(days=days_ago)
        request_params['shipDateStart'] = date_start.strftime('%Y-%m-%d')

        last_page = False
        page = 0
        while not last_page:
            if page:
                request_params['page'] = page
            page += 1
            response = requests.get(
                'https://ssapi.shipstation.com/shipments',
                params=request_params,
                auth=requests.auth.HTTPBasicAuth(settings.SHIPSTATION_API_KEY, settings.SHIPSTATION_API_SECRET),
            ).json()
            last_page = len(response['shipments']) < 100

            for row in response['shipments']:
                order_number = row['orderNumber']
                lead = Lead.objects.filter(account_name=order_number).first()
                if not lead:
                    orders_not_found.append(order_number)
                    continue

                if force:
                    lead.usps_tracking_code = None
                if not lead.usps_tracking_code:
                    orders_new.append(order_number)
                lead.update_from_shipstation(row)
                order_numbers.append(order_number)

        return JsonResponse({
            'result': True,
            'order_numbers': order_numbers,
            'orders_new': orders_new,
            'orders_not_found': orders_not_found,
            'days_ago': days_ago,
        })
