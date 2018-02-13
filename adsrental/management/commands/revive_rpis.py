from __future__ import unicode_literals

from multiprocessing.pool import ThreadPool
import datetime
import logging

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

from adsrental.models.lead import Lead
from adsrental.models.ec2_instance import EC2Instance


class Command(BaseCommand):
    help = 'Revive old EC2 EC2'

    def add_arguments(self, parser):
        parser.add_argument('--facebook', action='store_true')
        parser.add_argument('--google', action='store_true')
        parser.add_argument('--force', action='store_true')
        parser.add_argument('--threads', type=int, default=10)

    def revive(self, ec2_instance):
        info_str = ec2_instance.rpid + '\t' + ec2_instance.lead.name() + '\t' + ec2_instance.lead.email + '\t' + ec2_instance.lead.raspberry_pi.version
        netstat_out = ec2_instance.ssh_execute('netstat -an')
        if not netstat_out:
            print(info_str + '\t' + 'SSH down')
            return False
        if '1:2046' not in netstat_out and not self.force:
            print(info_str + '\t' + 'Tunnel down')
            return False

        cmd_to_execute = '''ssh pi@localhost -p 2046 "curl https://adsrental.com/static/update_pi.sh | bash"'''
        ec2_instance.ssh_execute(cmd_to_execute)
        print(info_str + '\t' + 'Attempted update')
        return True

    def handle(
        self,
        facebook,
        google,
        force,
        threads,
        **kwargs
    ):
        logging.raiseExceptions = False
        self.force = force
        ec2_instances = EC2Instance.objects.filter(lead__status__in=Lead.STATUSES_ACTIVE, lead__raspberry_pi__last_seen__gt=timezone.now() - datetime.timedelta(hours=1))

        if facebook:
            ec2_instances = ec2_instances.filter(lead__facebook_account=True)
        if google:
            ec2_instances = ec2_instances.filter(lead__google_account=True)

        ec2_instances = ec2_instances.exclude(lead__raspberry_pi__version=settings.RASPBERRY_PI_VERSION).select_related('lead', 'lead__raspberry_pi').order_by('-rpid')

        print 'Total', ec2_instances.count()

        pool = ThreadPool(processes=threads)
        results = pool.map(self.revive, ec2_instances)

        print('================')
        print(results)
        print('================')

        for ec2_instance in ec2_instances:
            new_ec2_instance = EC2Instance.objects.get(rpid=ec2_instance.rpid)
            if new_ec2_instance.lead.raspberry_pi.version == settings.RASPBERRY_PI_VERSION:
                info_str = ec2_instance.rpid + '\t' + ec2_instance.lead.name() + '\t' + ec2_instance.lead.email + '\t' + ec2_instance.lead.raspberry_pi.version
                print(info_str + '\t' + 'Updated')
