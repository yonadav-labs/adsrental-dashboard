from django.core.management.base import BaseCommand

from adsrental.models.ec2_instance import EC2Instance
from adsrental.utils import BotoResource


class Command(BaseCommand):
    help = 'Sync EC2 instances to DB'
    ec2_max_results = 300

    def handle(
        self,
        **kwargs
    ):
        boto_resource = BotoResource().get_resource()
        boto_instances = boto_resource.instances.filter(
            MaxResults=self.ec2_max_results,
        )

        ec2_instances = EC2Instance.objects.all()
        ec2_instance_map = {}
        for ec2_instance in ec2_instances:
            ec2_instance_map[ec2_instance.instance_id] = ec2_instance

        counter = 0
        for boto_instance in boto_instances:
            counter += 1
            print counter
            ec2_instance = ec2_instance_map.get(boto_instance.id)
            if not ec2_instance:
                EC2Instance.create_from_boto(boto_instance)
            else:
                ec2_instance.update_from_boto(boto_instance)
