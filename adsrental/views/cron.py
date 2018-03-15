from __future__ import unicode_literals

import os
import datetime

from django.core.cache import cache
from django.views import View
from django.http import JsonResponse
from django.conf import settings
from django_bulk_update.helper import bulk_update

from adsrental.models.ec2_instance import EC2Instance
from adsrental.models.lead import Lead
from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.models.lead_history import LeadHistory
from adsrental.models.lead_history_month import LeadHistoryMonth
from adsrental.utils import BotoResource


class SyncEC2View(View):
    '''
    Sync EC2 instances states from AWS to local DB.

    Parameters:

    * all - if 'true' syncs all EC2s
    * pending - if 'true' syncs only EC2s that have stopping or pending status in local DB
    * terminate_stopped - if 'true' terminates all instances that are currently stopped. Be careful.
    * missing - if 'true' creates instances for active leads if they are missing
    * execute - if 'true' performs all actions in AWS, otherwise it is test run
    '''
    ec2_max_results = 300

    def get(self, request):
        all = request.GET.get('all')
        pending = request.GET.get('pending')
        terminate_stopped = request.GET.get('terminate_stopped')
        missing = request.GET.get('missing')
        execute = request.GET.get('execute')

        if all:
            boto_resource = BotoResource().get_resource()
            ec2_instances = EC2Instance.objects.all()
            ec2_instances_map = {}
            for ec2_instance in ec2_instances:
                ec2_instances_map[ec2_instance.instance_id] = ec2_instance
            boto_instances = boto_resource.instances.filter(
                MaxResults=self.ec2_max_results,
            )

            counter = 0
            terminated_rpids = []
            deleted_rpids = []
            existing_instance_ids = []
            for boto_instance in boto_instances:
                counter += 1
                existing_instance_ids.append(boto_instance.id)
                instance = EC2Instance.upsert_from_boto(boto_instance, ec2_instances_map.get(boto_instance.id))
                if terminate_stopped:
                    if instance and instance.status == EC2Instance.STATUS_STOPPED and not instance.lead:
                        if execute:
                            instance.terminate()
                        terminated_rpids.append(instance.rpid)

            for instance in ec2_instances:
                if instance.instance_id not in existing_instance_ids:
                    deleted_rpids.append(instance.rpid)
                    instance.lead = None
                    instance.save()
                    instance.delete()

            return JsonResponse({
                'total': counter,
                'terminated_rpids': terminated_rpids,
                'deleted_rpids': deleted_rpids,
                'result': True,
            })
        if pending:
            boto_resource = BotoResource().get_resource()
            updated_rpids = []
            instances = EC2Instance.objects.filter(status__in=[EC2Instance.STATUS_PENDING, EC2Instance.STATUS_STOPPING])
            for instance in instances:
                if execute:
                    boto_instance = instance.get_boto_instance(boto_resource)
                    instance.update_from_boto(boto_instance)
                updated_rpids.append((instance.rpid, instance.status))

            return JsonResponse({
                'updated_rpids': updated_rpids,
                'result': True,
            })
        if missing:
            launched_rpids = []
            started_rpids = []
            instances = EC2Instance.objects.filter(lead__isnull=False).select_related('lead')
            for instance in instances:
                lead = instance.lead
                if lead.is_active() and not instance.is_running():
                    if execute:
                        instance.start(blocking=True)
                    started_rpids.append(instance.rpid)

            leads = Lead.objects.filter(status__in=Lead.STATUSES_ACTIVE, ec2instance__isnull=True).select_related('raspberry_pi', 'ec2instance')
            for lead in leads:
                if lead.is_active() and not lead.get_ec2_instance():
                    if execute:
                        EC2Instance.launch_for_lead(lead)
                    launched_rpids.append(lead.raspberry_id.rpid)

            return JsonResponse({
                'launched_rpids': launched_rpids,
                'started_rpids': started_rpids,
                'result': True,
            })


class LeadHistoryView(View):
    '''
    Calculate :model:`adsrental.Lead` stats and store them in :model:`adsrental.LeadHistory` and :model:`adsrental.LeadHistoryMonth`

    Parameters:

    * rpid - if provided, process only one lead, used for debug purposes
    * now - if 'true' creates or updates :model:`adsrental.LeadHistory` objects with current lead stats. Runs on cron hourly.
    * force - forde replace :model:`adsrental.LeadHistory` on run even if they are calculated
    * date - 'YYYY-MM-DD', if provided calculates :model:`adsrental.LeadHistory` from logs. Does not check worng password and potentially incaccurate.
    * aggregate - if 'true' calculates :model:`adsrental.LeadHistoryMonth`. You can also provide *date*
    '''
    def get(self, request):
        now = request.GET.get('now')
        force = request.GET.get('force')
        date = request.GET.get('date')
        rpid = request.GET.get('rpid')
        aggregate = request.GET.get('aggregate')
        results = []

        if now:
            leads = Lead.objects.filter(status__in=Lead.STATUSES_ACTIVE, raspberry_pi__isnull=False).select_related('raspberry_pi')
            if rpid:
                leads = leads.filter(raspberry_pi__rpid=rpid)
            for lead in leads:
                LeadHistory.upsert_for_lead(lead)
            return JsonResponse({
                'result': True,
            })
        if aggregate:
            leads = Lead.objects.filter(status__in=Lead.STATUSES_ACTIVE, raspberry_pi__isnull=False).select_related('raspberry_pi')
            if rpid:
                leads = leads.filter(raspberry_pi__rpid=rpid)
            d = datetime.datetime.strptime(date, settings.SYSTEM_DATE_FORMAT).date() if date else datetime.date.today()
            d = d.replace(day=1)
            for lead in leads:
                LeadHistoryMonth.get_or_create(lead=lead, date=d).aggregate()
            return JsonResponse({
                'result': True,
            })
        if date:
            leads = Lead.objects.filter(status__in=Lead.STATUSES_ACTIVE, raspberry_pi__isnull=False).select_related('raspberry_pi')
            if rpid:
                leads = leads.filter(raspberry_pi__rpid=rpid)
            d = datetime.datetime.strptime(date, settings.SYSTEM_DATE_FORMAT).date()
            if force:
                LeadHistory.objects.filter(date=d).delete()
            for lead in leads:
                if not force:
                    lead_history = LeadHistory.objects.filter(lead=lead, date=d).first()
                    if lead_history:
                        continue

                log_filename = '{}.log'.format(d.strftime('%Y%m%d'))
                log_path = os.path.join(settings.RASPBERRY_PI_LOG_PATH, lead.raspberry_pi.rpid, log_filename)
                is_online = os.path.exists(log_path)
                LeadHistory(lead=lead, date=d, checks_online=24 if is_online else 0, checks_offline=24 if not is_online else 0).save()
                # print lead, is_online
                results.append([lead.email, is_online])

            return JsonResponse({
                'results': results,
                'result': True,
            })


class UpdatePingView(View):
    '''
    Update :model:`adsrental.RaspberryPi` and :model:`adsrental.EC2Instance` pings in databse from cache.

    Runs every 2 minutes by cron.

    Parameters:

    * rpid - if provided, process only one lead, used for debug purposes
    '''
    def get(self, request):
        ping_keys = cache.get('ping_keys', [])
        rpid = request.GET.get('rpid')
        if rpid:
            ping_keys = [RaspberryPi.get_ping_key(rpid)]

        rpids_ping_map = {}
        for ping_key in ping_keys:
            ping_data = cache.get(ping_key)
            if not ping_data:
                continue
            if ping_data.get('v') != settings.CACHE_VERSION:
                continue
            rpid = ping_data['rpid']
            rpids_ping_map[rpid] = ping_data

        raspberry_pis = RaspberryPi.objects.filter(rpid__in=rpids_ping_map.keys())
        ec2_instances = EC2Instance.objects.filter(rpid__in=rpids_ping_map.keys())
        ec2_instances_map = {}
        for ec2_instance in ec2_instances:
            ec2_instances_map[ec2_instance.rpid] = ec2_instance
        for raspberry_pi in raspberry_pis:
            ping_data = rpids_ping_map.get(raspberry_pi.rpid)
            rpid = ping_data['rpid']
            ip_address = ping_data['ip_address']
            version = ping_data['raspberry_pi_version']
            restart_required = ping_data['restart_required']
            last_ping = ping_data.get('last_ping')
            last_troubleshoot = ping_data.get('last_troubleshoot')

            if last_ping:
                raspberry_pi.update_ping(last_ping)
            if raspberry_pi.ip_address != ip_address:
                raspberry_pi.ip_address = ip_address
            if raspberry_pi.version != version:
                raspberry_pi.version = version
            if restart_required:
                raspberry_pi.restart_required = False
            raspberry_pi.version = version
            ec2_instance = ec2_instances_map.get(rpid)

            if ec2_instance and last_troubleshoot:
                if not ec2_instance.last_troubleshoot or ec2_instance.last_troubleshoot < last_troubleshoot:
                    ec2_instance.last_troubleshoot = last_ping
                    if ping_data.get('tunnel_up'):
                        ec2_instance.tunnel_up_date = last_ping
                        ec2_instance.tunnel_up = True

        bulk_update(raspberry_pis, update_fields=['ip_address', 'first_seen', 'first_tested', 'online_since_date', 'last_seen', 'version'])
        bulk_update(ec2_instances, update_fields=['last_troubleshoot', 'tunnel_up_date'])
        return JsonResponse({
            'ping_keys': ping_keys,
            'result': True,
        })
