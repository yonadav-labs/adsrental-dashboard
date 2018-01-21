import time

from django.core.management.base import BaseCommand
from django.conf import settings
import boto3

from adsrental.models.lead import Lead


class Command(BaseCommand):
    help = 'Start and shutdown EC2'
    ec2_max_results = 300

    def add_arguments(self, parser):
        parser.add_argument('--launch-required', action='store_true')
        parser.add_argument('--launch-missing', action='store_true')
        parser.add_argument('--stop-banned', action='store_true')
        parser.add_argument('--stop-duplicates', action='store_true')
        parser.add_argument('--stop-not-found', action='store_true')
        parser.add_argument('--terminate-stopped', action='store_true')
        parser.add_argument('--fix-ips', action='store_true')
        parser.add_argument('--execute', action='store_true')
        parser.add_argument('--progress', action='store_true')

    def get_instance_tag(self, instance, key):
        if not instance.tags:
            return None

        for tagpair in instance.tags:
            if tagpair['Key'] == key:
                return tagpair['Value']

        return None

    def set_instance_tag(self, boto_client, instance, key, value):
        tags = instance.tags or []
        key_found = False
        for tagpair in tags:
            if tagpair['Key'] == key:
                key_found = True
                tagpair['Value'] = value
                break
        if not key_found:
            tags.append({'Key': key, 'Value': value})

        try:
            boto_client.create_tags(Resources=[instance.id], Tags=tags)
        except:
            print 'Cound not add tag for', instance.id, key, '=', value
            pass

    def handle(
        self,
        launch_required,
        launch_missing,
        stop_banned,
        stop_duplicates,
        stop_not_found,
        terminate_stopped,
        fix_ips,
        execute,
        progress,
        **kwargs
    ):
        boto_client = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        ).resource('ec2', region_name=settings.AWS_REGION)

        leads = Lead.objects.filter(raspberry_pi__isnull=False).select_related('raspberry_pi')
        required_leads = [i for i in leads if i.status in (Lead.STATUS_QUALIFIED, Lead.STATUS_IN_PROGRESS, Lead.STATUS_AVAILABLE)]
        # rpids = [i.raspberry_pi.name for i in leads if i.raspberry_pi]
        # required_rpids = [i.raspberry_pi.rpid for i in leads if i.raspberry_pi and i.status in ('Qualified', 'In-Progress')]
        # banned_rpids = [i.raspberry_pi.rpid for i in leads if i.raspberry_pi and i.status == 'Banned']
        leads_rpid_map = {}
        for lead in leads:
            leads_rpid_map[lead.raspberry_pi.rpid] = lead
        launched_rpid = []

        stopped_rpids = []
        terminated_rpids = []
        started_rpids = []
        duplicate_rpids = []
        running_rpids = []
        instance_states_counter = {
            'running': 0,
            'stopping': 0,
            'terminated': 0,
            'stopped': 0,
            'pending': 0,
        }

        # print banned_rpids

        instances = boto_client.instances.filter(
            MaxResults=self.ec2_max_results,
        )
        for counter, instance in enumerate(instances):
            if progress and counter % 100 == 0:
                print '{} instances processed'.format(counter)

            instance_id = instance.id
            public_dns_name = instance.public_dns_name
            public_ip_address = instance.public_ip_address
            instance_rpid = None
            instance_state = instance.state['Name']
            instance_states_counter[instance_state] += 1

            if instance_state == 'terminated':
                continue

            instance_rpid = self.get_instance_tag(instance, 'Name')
            is_duplicate = self.get_instance_tag(instance, 'Duplicate') == 'true'
            instance_lead_email = self.get_instance_tag(instance, 'Email')
            if is_duplicate and instance_state == 'running':
                print 'DUPLICATE:', public_dns_name, instance_rpid, ', stopping'
                continue

            if not instance_rpid or not instance_rpid.startswith('RP'):
                # print 'Unknown instance', public_dns_name, instance_rpid
                continue

            if is_duplicate or instance_rpid in running_rpids:
                if stop_duplicates and not is_duplicate:
                    print 'MARK DUPLICATE:', public_dns_name, instance_rpid, ', adding duplicate tag'
                    if execute:
                        self.set_instance_tag(boto_client, instance, 'Duplicate', 'true')
                if stop_duplicates and instance_state == 'running':
                    print 'DUPLICATE:', public_dns_name, instance_rpid, ', stopping'
                    duplicate_rpids.append(instance_rpid)
                    if execute:
                        instance.stop()
                continue

            launched_rpid.append(instance_rpid)
            if instance_state == 'running':
                running_rpids.append(instance_rpid)

            lead = leads_rpid_map.get(instance_rpid)
            if terminate_stopped and not lead and instance_state == 'stopped':
                print 'NO LEAD (TERM):', instance_id, instance_rpid, ' has no corresponding lead and it is', instance_state, ', terminating'
                if execute:
                    instance.terminate()
                continue

            if terminate_stopped and not lead and instance_state == 'running':
                print 'NO LEAD:', instance_id, instance_rpid, ' has no corresponding lead and it is', instance_state, ', stopping'
                if execute:
                    instance.stop()
                continue

            if not lead:
                continue

            if not instance_lead_email and lead.email:
                print 'ADD EMAIL:', instance_id, instance_rpid, ' add tag Email =', lead.email
                if execute:
                    self.set_instance_tag(boto_client, instance, 'Email', lead.email)

            if terminate_stopped and lead.status in [Lead.STATUS_BANNED] and instance_state == 'stopped':
                print 'BANNED (TERM):', instance_id, instance_rpid, ' belongs to banned lead and it is ', instance_state, ', terminating'
                terminated_rpids.append(instance_rpid)
                if execute:
                    instance.terminate()
                continue

            if launch_required and lead.status in [Lead.STATUS_IN_PROGRESS, Lead.STATUS_QUALIFIED, Lead.STATUS_AVAILABLE] and instance_state == 'stopped':
                if instance_state == 'stopped':
                    print 'START:', instance_id, instance_rpid, 'should be running, but it is', instance_state, ', starting'
                    started_rpids.append(instance_rpid)
                    if execute:
                        instance.start()
                else:
                    print instance_id, instance_rpid, 'should be running, but it is', instance_state, ', skipping'

            if stop_banned and lead.status == Lead.STATUS_BANNED and instance_state == 'running':
                print 'BANNED:', instance_id, instance_rpid, 'is now', instance_state, ', stopping'
                stopped_rpids.append(instance_rpid)
                if execute:
                    instance.stop()

            if fix_ips and lead.raspberry_pi.ec2_hostname != public_dns_name and public_dns_name:
                print 'DATA: Updating data for RPID', instance_rpid, ', old:', lead.raspberry_pi.ec2_hostname, 'new:', public_dns_name
                lead.raspberry_pi.ec2_hostname = public_dns_name
                lead.raspberry_pi.ipaddress = public_ip_address
                lead.raspberry_pi.save()

        print 'Finished EC2 processing'

        if launch_missing:
            for lead in required_leads:
                rpid = lead.raspberry_pi.rpid
                if rpid in launched_rpid:
                    continue
                print 'START NEW:', rpid, 'will be launched for', lead.email
                if execute:
                    boto_client.create_instances(
                        ImageId=settings.AWS_IMAGE_AMI,
                        MinCount=1,
                        MaxCount=1,
                        KeyName='AI Farming Key',
                        InstanceType='t2.micro',
                        SecurityGroupIds=settings.AWS_SECURITY_GROUP_IDS,
                        UserData=rpid,
                        TagSpecifications=[
                            {
                                'ResourceType': 'instance',
                                'Tags': [
                                    {
                                        'Key': 'Name',
                                        'Value': rpid,
                                    },
                                    {
                                        'Key': 'Email',
                                        'Value': lead.email,
                                    },
                                    {
                                        'Key': 'Duplicate',
                                        'Value': 'false',
                                    },
                                ]
                            },
                        ],
                    )
                started_rpids.append(rpid)

        if stopped_rpids:
            print 'Stopped', len(stopped_rpids), stopped_rpids
        if terminated_rpids:
            print 'Terminated', len(terminated_rpids), terminated_rpids
        if started_rpids:
            print 'Started', len(started_rpids), started_rpids
        if duplicate_rpids:
            print 'Duplicates', len(duplicate_rpids), duplicate_rpids
        print instance_states_counter
        print time.clock(), 'finished'
