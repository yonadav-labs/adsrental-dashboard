from django.views import View
from django.http import JsonResponse

from adsrental.models.ec2_instance import EC2Instance
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

    def _handler_process_all(self, terminate_stopped, execute):
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
            status = boto_instance.state['Name']
            if status == EC2Instance.STATUS_TERMINATED:
                continue
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

    def _handler_pending(self, execute):
        updated_rpids = []
        boto_resource = BotoResource()
        for ec2_boto in boto_resource.get_resource('ec2').instances.all():
            ec2 = EC2Instance.objects.filter(instance_id=ec2_boto.id).first()
            if ec2:
                if execute:
                    ec2.update_from_boto(ec2_boto)
                updated_rpids.append(ec2.rpid or '<NORPID>')

        return JsonResponse({
            'updated_rpids': sorted(updated_rpids),
            'result': True,
        })

    def _handler_missing(self, execute):
        launched_rpids = []
        started_rpids = []
        instances = EC2Instance.objects.filter(lead__isnull=False).select_related('lead')
        for instance in instances:
            lead = instance.lead
            if lead.is_active() and not instance.is_running():
                if execute:
                    instance.start(blocking=True)
                started_rpids.append(instance.rpid)

        return JsonResponse({
            'launched_rpids': launched_rpids,
            'started_rpids': started_rpids,
            'result': True,
        })

    def get(self, request):
        process_all = request.GET.get('all') == 'true'
        pending = request.GET.get('pending')
        terminate_stopped = request.GET.get('terminate_stopped')
        missing = request.GET.get('missing')
        execute = request.GET.get('execute')

        if process_all:
            return self._handler_process_all(terminate_stopped, execute)

        if pending:
            return self._handler_pending(execute)

        if missing:
            return self._handler_missing(execute)

        return JsonResponse({
            'result': False,
        })
