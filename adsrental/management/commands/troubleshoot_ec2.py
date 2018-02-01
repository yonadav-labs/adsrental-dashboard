from multiprocessing.pool import ThreadPool
from itertools import chain, islice
import datetime

from django.db import connection
from django.utils import timezone
from django.core.management.base import BaseCommand

from adsrental.models.lead import Lead


def chunks(iterable, size=10):
    iterator = iter(iterable)
    for first in iterator:
        yield chain([first], islice(iterator, size - 1))


def troubleshoot(args):
    lead, fix = args
    ec2_instance = lead.get_ec2_instance()
    if ec2_instance:
        ec2_instance.troubleshoot()
        # if fix:
        #     ec2_instance.troubleshoot_fix()
    connection.close()
    return lead, ec2_instance


class Command(BaseCommand):
    help = 'Troubleshoot EC2 instances to DB'

    def add_arguments(self, parser):
        parser.add_argument('--fix', action='store_true')
        parser.add_argument('--threads', type=int, default=20)
        parser.add_argument('--chunk-size', type=int, default=20)
        parser.add_argument('--older-minutes', type=int, default=0)
        parser.add_argument('--online-only', action='store_true')
        parser.add_argument('--tunnel-only', action='store_true')
        parser.add_argument('--ssh-only', action='store_true')
        parser.add_argument('--web-only', action='store_true')
        parser.add_argument('--skip', type=int, default=0)

    def handle(
        self,
        fix,
        threads,
        chunk_size,
        older_minutes,
        online_only,
        tunnel_only,
        ssh_only,
        web_only,
        skip,
        **kwargs
    ):
        leads = Lead.objects.filter(
            raspberry_pi__isnull=False,
            status__in=Lead.STATUSES_ACTIVE,
        )
        if older_minutes:
            leads = leads.filter(
                ec2instance__last_troubleshoot___lt=timezone.now() - datetime.timedelta(minutes=older_minutes),
            )
        if tunnel_only:
            leads = leads.filter(
                ec2instance__tunnel_up=False,
            )
        if ssh_only:
            leads = leads.filter(
                ec2instance__ssh_up=False,
            )
        if web_only:
            leads = leads.filter(
                ec2instance__web_up=False,
            )
        leads = [i for i in leads.order_by('ec2instance__last_troubleshoot').select_related('ec2instance', 'raspberry_pi')]
        if online_only:
            leads = [i for i in leads if i.raspberry_pi.online()]
        if skip:
            leads = leads[skip:]
            print 'Skip first', skip, 'entries'
        total = len(leads)
        counter = 0
        for lead_chunk in chunks(leads, chunk_size):
            pool = ThreadPool(processes=threads)
            lead_queue = [(i, fix) for i in lead_chunk]
            print 'Start pool: {} / {}'.format(counter, total)
            results = pool.map(troubleshoot, lead_queue)
            counter += len(lead_queue)
            for lead, ec2_instance in results:
                if not ec2_instance:
                    print lead.email, 'no ec2'
                    continue

                print lead.email, ec2_instance.ssh_up, ec2_instance.web_up, ec2_instance.tunnel_up
