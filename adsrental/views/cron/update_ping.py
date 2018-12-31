from django.core.cache import cache
from django.views import View
from django.http import JsonResponse
from django_bulk_update.helper import bulk_update

from adsrental.models.ec2_instance import EC2Instance
from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.utils import PingCacheHelper


class UpdatePingView(View):
    '''
    Update :model:`adsrental.RaspberryPi` and :model:`adsrental.EC2Instance` pings in databse from cache.

    Runs every 2 minutes by cron.

    Parameters:

    * rpid - if provided, process only one lead, used for debug purposes
    '''

    def get(self, request):
        ping_cache_helper = PingCacheHelper()
        ping_keys = cache.get('ping_keys', [])
        rpid = request.GET.get('rpid')
        if rpid:
            ping_keys = [ping_cache_helper.get_key(rpid)]

        rpids_ping_map = {}
        for ping_key in ping_keys:
            ping_data = cache.get(ping_key)
            if not ping_data:
                continue
            rpid = ping_data['rpid']
            rpids_ping_map[rpid] = ping_data

        rpids = []
        invalidated_rpids = []
        raspberry_pis = RaspberryPi.objects.filter(rpid__in=rpids_ping_map.keys()).prefetch_related('lead')
        ec2_instances = EC2Instance.objects.filter(rpid__in=rpids_ping_map.keys()).select_related('lead')
        ec2_instances_map = {}
        for ec2_instance in ec2_instances:
            ec2_instances_map[ec2_instance.rpid] = ec2_instance
        for raspberry_pi in raspberry_pis:
            ping_data = rpids_ping_map.get(raspberry_pi.rpid)
            rpid = ping_data['rpid']
            rpids.append(rpid)
            ec2_instance = ec2_instances_map.get(rpid)
            self.process_ping_data(ping_data, raspberry_pi, ec2_instance)

            if not ping_cache_helper.is_data_consistent(
                    ping_data,
                    raspberry_pi=raspberry_pi,
                    ec2_instance=ec2_instance,
            ):
                ping_cache_helper.delete(rpid)
                invalidated_rpids.append(rpid)

        bulk_update(raspberry_pis, update_fields=['ip_address', 'first_seen', 'first_tested', 'online_since_date', 'last_seen', 'version'])
        bulk_update(ec2_instances, update_fields=['last_troubleshoot', 'tunnel_up_date'])
        return JsonResponse({
            'rpids': rpids,
            'invalidated': invalidated_rpids,
            'result': True,
        })

    def process_ping_data(self, ping_data, raspberry_pi, ec2_instance):
        raspberry_pi.process_ping_data(ping_data)

        last_troubleshoot = ping_data.get('last_troubleshoot')
        tunnel_up = ping_data.get('tunnel_up')
        if ec2_instance and last_troubleshoot:
            if not ec2_instance.last_troubleshoot or ec2_instance.last_troubleshoot < last_troubleshoot:
                ec2_instance.last_troubleshoot = last_troubleshoot
                if tunnel_up:
                    ec2_instance.tunnel_up_date = last_troubleshoot
                    ec2_instance.tunnel_up = True
