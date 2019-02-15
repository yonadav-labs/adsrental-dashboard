import datetime

import requests
from django.views import View
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone

from adsrental.models.lead import Lead


class SyncFromShipStationView(View):
    '''
    Get shipments from shipstation API and populate *usps_tracking_code* in :model:`adsrental.Lead` identified by *shipstation_order_number*.
    Runs hourly by cron.

    Parameters:

    * days_ago - Get orders that were created X days ago. If not provided, gets orders 1 day ago.
    * force - if 'true' removes tracking codes that are not present in SS.
    '''

    def get(self, request):
        order_numbers = []
        orders_new = []
        orders_not_found = []
        orders_found = []
        orders_status_updated = []
        days_ago = int(request.GET.get('days_ago', '1'))
        force = request.GET.get('force', '') == 'true'
        find = request.GET.get('find', '') == 'true'
        request_params = {}
        date_start = timezone.now() - datetime.timedelta(days=days_ago)
        request_params['shipDateStart'] = date_start.strftime(settings.SYSTEM_DATE_FORMAT)

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

            if 'shipments' not in response:
                break

            last_page = len(response['shipments']) < 100

            for row in response['shipments']:
                order_number = row['orderNumber']
                rpid = order_number.split('__')[0]
                lead = Lead.objects.filter(shipstation_order_number=order_number).first()

                if find and not lead:
                    lead = Lead.objects.filter(shipstation_order_number=None, raspberry_pi__rpid=rpid).first()
                    if lead:
                        lead.shipstation_order_number = order_number
                        lead.save()
                        orders_found.append(order_number)

                if not lead:
                    orders_not_found.append(order_number)
                    continue

                if force:
                    lead.usps_tracking_code = None
                if not lead.usps_tracking_code:
                    orders_new.append(order_number)
                lead.update_from_shipstation(row)
                order_numbers.append(order_number)

        last_page = False
        page = 0
        request_params = {}
        request_params['modifyDateStart'] = date_start.strftime(settings.SYSTEM_DATE_FORMAT)
        while not last_page:
            if page:
                request_params['page'] = page
            page += 1
            response = requests.get(
                'https://ssapi.shipstation.com/orders',
                params=request_params,
                auth=requests.auth.HTTPBasicAuth(settings.SHIPSTATION_API_KEY, settings.SHIPSTATION_API_SECRET),
            ).json()
            last_page = len(response['orders']) < 100
            for row in response['orders']:
                order_number = row['orderNumber']
                rpid = order_number.split('__')[0]
                lead = Lead.objects.filter(shipstation_order_number=order_number).first()

                if find and not lead:
                    lead = Lead.objects.filter(shipstation_order_number=None, raspberry_pi__rpid=rpid).first()
                    if lead:
                        lead.shipstation_order_number = order_number
                        lead.save()
                        orders_found.append(order_number)

                if not lead:
                    orders_not_found.append(order_number)
                    continue

                if lead.shipstation_order_status != row['orderStatus']:
                    lead.shipstation_order_status = row['orderStatus']
                    lead.save()
                    orders_status_updated.append(order_number)

        return JsonResponse({
            'result': True,
            'order_numbers': order_numbers,
            'orders_new': orders_new,
            'orders_found': orders_found,
            'orders_not_found': orders_not_found,
            'orders_status_updated': orders_status_updated,
            'days_ago': days_ago,
        })
