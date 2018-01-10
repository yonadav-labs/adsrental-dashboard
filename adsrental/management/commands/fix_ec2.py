import time

from django.core.management.base import BaseCommand
from django.conf import settings
import boto3

from salesforce_handler.models import Lead as SFLead


class Command(BaseCommand):
    help = 'Start and shutdown EC2'
    ec2_max_results = 300

    def add_arguments(self, parser):
        parser.add_argument('--terminate', action='store_true')
        parser.add_argument('--stop', action='store_true')
        parser.add_argument('--launch', action='store_true')

    def handle(self, terminate, stop, launch, *args, **options):
        boto_client = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        ).resource('ec2', region_name=settings.AWS_REGION)

        print time.clock(), 'Starting'

        leads = SFLead.objects.filter().simple_select_related('raspberry_pi')
        # rpids = [i.raspberry_pi.name for i in leads if i.raspberry_pi]
        required_rpids = [i.raspberry_pi.name for i in leads if i.raspberry_pi and i.status in ('Qualified', 'In-Progress')]
        banned_rpids = [i.raspberry_pi.name for i in leads if i.raspberry_pi and i.status == 'Banned']
        launched_rpid = []

        stopped_rpids = []
        started_rpids = []

        print time.clock(), 'Got SF data, {} insstances has to be existing'.format(len(required_rpids))

        # print banned_rpids

        instances = boto_client.instances.all()
        for counter, instance in enumerate(instances):
            if not counter:
                print time.clock(), 'Got instances'
            # elif counter % 100 == 0:
            #     print '{} instances processed'.format(counter)

            instance_id = instance.id
            public_dns_name = instance.public_dns_name
            instance_rpid = None
            instance_state = instance.state['Name']

            if instance.tags:
                for tagpair in instance.tags:
                    if tagpair['Key'] == 'Name':
                        instance_rpid = tagpair['Value']
            else:
                print instance_id, public_dns_name, instance_rpid, instance_state, 'will be stopped as it has no tags'
                if terminate:
                    instance.terminate()
                if stop:
                    instance.stop()

            if instance_rpid:
                launched_rpid.append(instance_rpid)

            if not instance_rpid or not instance_rpid.startswith('RP'):
                continue

            launched_rpid.append(instance_rpid)

            if instance_rpid not in required_rpids:
                print instance_id, public_dns_name, instance_rpid, instance_state, 'will be stopped'
                if terminate:
                    instance.terminate()
                if stop:
                    instance.stop()
                stopped_rpids.append(instance_rpid)

        for rpid in required_rpids:
            if rpid in banned_rpids:
                continue
            if rpid in launched_rpid:
                continue
            print rpid, 'will be launched'
            if launch:
                boto_client.create_instances(
                    ImageId='ami-68e20f10',
                    MinCount=1,
                    MaxCount=1,
                    KeyName='AI Farming Key',
                    InstanceType='t2.micro',
                    SecurityGroupIds=['sg-18528a63'],
                    UserData=rpid,
                    TagSpecifications=[
                        {
                            'ResourceType': 'instance',
                            'Tags': [
                                {
                                    'Key': 'Name',
                                    'Value': rpid,
                                },
                            ]
                        },
                    ],
                )
            started_rpids.append(rpid)

        print 'Stopped', stopped_rpids
        print 'Lauched', started_rpids
        print 'Total', len(launched_rpid) + len(started_rpids)
        print time.clock(), 'finished'
