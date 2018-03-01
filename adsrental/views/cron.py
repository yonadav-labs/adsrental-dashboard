from __future__ import unicode_literals

import os
import datetime

from django.views import View
from django.http import JsonResponse
from django.conf import settings

from adsrental.models.ec2_instance import EC2Instance
from adsrental.models.lead import Lead
from adsrental.models.lead_history import LeadHistory
from adsrental.models.lead_history_month import LeadHistoryMonth
from adsrental.utils import BotoResource


class SyncEC2View(View):
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
    def get(self, request):
        now = request.GET.get('now')
        force = request.GET.get('force')
        date = request.GET.get('date')
        aggregate = request.GET.get('aggregate')

        if now:
            leads = Lead.objects.filter(status__in=Lead.STATUSES_ACTIVE, raspberry_pi__isnull=False).select_related('raspberry_pi')
            for lead in leads:
                LeadHistory.upsert_for_lead(lead)
            return JsonResponse({
                'result': True,
            })
        if aggregate:
            leads = Lead.objects.filter(status__in=Lead.STATUSES_ACTIVE, raspberry_pi__isnull=False).select_related('raspberry_pi')
            d = datetime.datetime.strptime(date, settings.SYSTEM_DATE_FORMAT).date() if date else datetime.date.today()
            d = d.replace(day=1)
            for lead in leads:
                LeadHistoryMonth.get_or_create(lead=lead, date=d).aggregate()
            return JsonResponse({
                'result': True,
            })
        if date:
            leads = Lead.objects.filter(status__in=Lead.STATUSES_ACTIVE, raspberry_pi__isnull=False).select_related('raspberry_pi')
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
            return JsonResponse({
                'result': True,
            })
