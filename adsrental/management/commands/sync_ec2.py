from django.core.management.base import BaseCommand

from adsrental.models.ec2_instance import EC2Instance
from adsrental.utils import BotoResource


class Command(BaseCommand):
    help = 'Sync EC2 instances to DB'
    ec2_max_results = 300

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true')
        parser.add_argument('--pending', action='store_true')

    def handle(
        self,
        all,
        pending,
        **kwargs
    ):
        boto_resource = BotoResource().get_resource()
        if all:
            boto_instances = boto_resource.instances.filter(
                MaxResults=self.ec2_max_results,
            )

            counter = 0
            for boto_instance in boto_instances:
                counter += 1
                if counter % 100 == 0:
                    print 'PROCESSED:', counter
                EC2Instance.upsert_from_boto(boto_instance)

        if pending:
            instances = EC2Instance.objects.filter(status__in=[EC2Instance.STATUS_PENDING, EC2Instance.STATUS_STOPPING])
            for instance in instances:
                boto_instance = instance.get_boto_instance(boto_resource)
                instance.update_from_boto(boto_instance)
                print 'UPDATED:', instance
