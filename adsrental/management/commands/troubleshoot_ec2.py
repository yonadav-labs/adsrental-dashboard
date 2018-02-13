from __future__ import unicode_literals

from multiprocessing.pool import ThreadPool
from itertools import chain, islice
import datetime
import time

from django.db import connection
from django.utils import timezone
from django.core.management.base import BaseCommand

from adsrental.models.lead import Lead


def chunks(iterable, size=10):
    iterator = iter(iterable)
    for first in iterator:
        yield chain([first], islice(iterator, size - 1))


def troubleshoot(args):
    t = time.time()
    lead, fix = args
    ec2_instance = lead.get_ec2_instance()
    if ec2_instance:
        try:
            ec2_instance.troubleshoot()
        except:
            print 'ERROR', lead.email
    connection.close()
    print lead.email, 'UP' if ec2_instance and ec2_instance.tunnel_up else 'DOWN', 'took', int(time.time() - t), 'seconds'
    return lead


class Command(BaseCommand):
    help = 'Troubleshoot EC2 instances to DB'

    def add_arguments(self, parser):
        parser.add_argument('--fix', action='store_true')
        parser.add_argument('--threads', type=int, default=20)
        parser.add_argument('--chunk-size', type=int, default=20)
        parser.add_argument('--older-minutes', type=int, default=0)
        parser.add_argument('--online-only', action='store_true')
        parser.add_argument('--tunnel-only', action='store_true')
        parser.add_argument('--skip', type=int, default=0)

    def handle(
        self,
        fix,
        threads,
        chunk_size,
        older_minutes,
        online_only,
        tunnel_only,
        skip,
        **kwargs
    ):
        leads = Lead.objects.filter(
            raspberry_pi__isnull=False,
            status__in=Lead.STATUSES_ACTIVE,
        )
        if older_minutes:
            leads = leads.filter(
                ec2instance__last_troubleshoot__lt=timezone.now() - datetime.timedelta(minutes=older_minutes),
            )
        if tunnel_only:
            leads = leads.filter(
                ec2instance__tunnel_up=False,
            )
        if online_only:
            leads = leads.filter(
                raspberry_pi__last_seen__gt=timezone.now() - datetime.timedelta(minutes=3),
            )
        leads = [i for i in leads.order_by('ec2instance__last_troubleshoot').select_related('ec2instance', 'raspberry_pi')]
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
            for lead in results:
                pass
