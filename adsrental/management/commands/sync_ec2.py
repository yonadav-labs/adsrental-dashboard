from django.core.management.base import BaseCommand

from adsrental.models.ec2_instance import EC2Instance
from adsrental.models.lead import Lead
from adsrental.utils import BotoResource


class Command(BaseCommand):
    help = 'Sync EC2 instances to DB'
    ec2_max_results = 300

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true')
        parser.add_argument('--pending', action='store_true')
        parser.add_argument('--terminate-stopped', action='store_true')
        parser.add_argument('--missing', action='store_true')

    def handle(
        self,
        all,
        pending,
        terminate_stopped,
        missing,
        **kwargs
    ):
        boto_resource = BotoResource().get_resource()
        if all:
            boto_instances = boto_resource.instances.filter(
                MaxResults=self.ec2_max_results,
            )

            counter = 0
            instance_ids = []
            for boto_instance in boto_instances:
                counter += 1
                if counter % 100 == 0:
                    print 'PROCESSED:', counter
                instance_ids.append(boto_instance.id)
                instance = EC2Instance.upsert_from_boto(boto_instance)
                if terminate_stopped:
                    if instance and instance.status == EC2Instance.STATUS_STOPPED and not instance.lead:
                        print 'TERMINATE:', instance.lead, instance.email, instance.rpid, instance.is_duplicate
                        instance.terminate()

            instances = EC2Instance.objects.all()
            for instance in instances:
                if instance.instance_id not in instance_ids:
                    instance.lead = None
                    instance.save()
                    instance.delete()

        if pending:
            instances = EC2Instance.objects.filter(status__in=[EC2Instance.STATUS_PENDING, EC2Instance.STATUS_STOPPING])
            for instance in instances:
                boto_instance = instance.get_boto_instance(boto_resource)
                instance.update_from_boto(boto_instance)
                print 'UPDATED:', instance

        if missing:
            instances = EC2Instance.objects.all().select_related('lead')
            for instance in instances:
                lead = instance.lead
                if lead.is_active() and not instance.is_running():
                    instance.start(blocking=True)
                    print 'UPDATED:', instance

            leads = Lead.objects.all().select_related('raspberry_pi', 'ec2instance')
            for lead in leads:
                if lead.is_active() and not lead.get_ec2_instance():
                    EC2Instance.launch_for_lead(lead)
                    print 'NEW:', lead.email
