from __future__ import unicode_literals

from django.views import View
from django.http import JsonResponse

from adsrental.models.ec2_instance import EC2Instance
from adsrental.models.lead import Lead
from adsrental.utils import BotoResource


class SyncEC2View(View):
    def get(self, request, rpid):
        all = request.GET.get('all')
        pending = request.GET.get('pending')
        terminate_stopped = request.GET.get('terminate_stopped')
        missing = request.GET.get('missing')
        execute = request.GET.get('execute')

        boto_resource = BotoResource().get_resource()
        if all:
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
            updated_rpids = []
            instances = EC2Instance.objects.filter(status__in=[EC2Instance.STATUS_PENDING, EC2Instance.STATUS_STOPPING])
            for instance in instances:
                if execute:
                    boto_instance = instance.get_boto_instance(boto_resource)
                    instance.update_from_boto(boto_instance)
                updated_rpids.append((instance.rpid, instance.status))

                return JsonResponse({
                    'total': counter,
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
                'total': counter,
                'launched_rpids': launched_rpids,
                'started_rpids': started_rpids,
                'result': True,
            })
