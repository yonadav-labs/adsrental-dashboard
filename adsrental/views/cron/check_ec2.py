import datetime
from multiprocessing.pool import ThreadPool

from django.views import View
from django.http import JsonResponse
from django.utils import timezone

from adsrental.models.ec2_instance import EC2Instance
from adsrental.utils import BotoResource


class CheckEC2View(View):
    '''
    Check :model:`adsrental.EC2Instance` if they have action RDP session, stops them otherwise.
    '''
    MAX_ESSENTIAL_RUNNING = 2

    def get(self, request):
        online_ec2s = []
        stopped_ec2s = []
        stopping_instances = []
        stopping_essential_ec2s = []
        online_essential_ec2s = []
        unassigned_essential_ec2s = []
        now = timezone.localtime(timezone.now())
        ec2_client = BotoResource().get_client('ec2')
        pool = ThreadPool(processes=10)
        ec2_instances = EC2Instance.objects.filter(
            last_rdp_start__lt=now - datetime.timedelta(minutes=15),
            status=EC2Instance.STATUS_RUNNING,
            is_essential=False,
        )
        results = pool.map(lambda x: [x, x.is_rdp_session_active()], ec2_instances)
        for ec2_instance, is_rdp_session_active in results:
            if is_rdp_session_active:
                ec2_instance.last_rdp_start = now
                ec2_instance.save()
                online_ec2s.append(ec2_instance.rpid)
            else:
                stopped_ec2s.append(ec2_instance.rpid)
                stopping_instances.append(ec2_instance)

        ec2_instances = EC2Instance.objects.filter(
            last_rdp_start__lt=now - datetime.timedelta(minutes=15),
            status=EC2Instance.STATUS_RUNNING,
            is_essential=True,
        )
        essential_running_counter = 0
        results = pool.map(lambda x: [x, x.is_rdp_session_active()], ec2_instances)
        for ec2_instance, is_rdp_session_active in results:
            if is_rdp_session_active:
                ec2_instance.last_rdp_start = now
                ec2_instance.save()
                online_essential_ec2s.append(ec2_instance.rpid)
            else:
                essential_running_counter += 1
                unassigned_essential_ec2s.append(ec2_instance.rpid or ec2_instance.essential_key)
                ec2_instance.unassign_essential()
                if essential_running_counter > self.MAX_ESSENTIAL_RUNNING:
                    ec2_instance.stop()
                    stopping_essential_ec2s.append(ec2_instance.rpid)

        if stopping_instances:
            ec2_client.stop_instances(InstanceIds=[ec2.instance_id for ec2 in stopping_instances])
            for ec2 in stopping_instances:
                ec2.status = EC2Instance.STATUS_STOPPED
                ec2.save()

        return JsonResponse({
            'result': True,
            'online_ec2s': online_ec2s,
            'stopped_ec2s': stopped_ec2s,
            'stopping_essential_ec2s': stopping_essential_ec2s,
            'online_essential_ec2s': online_essential_ec2s,
            'unassigned_essential_ec2s': unassigned_essential_ec2s,
        })
