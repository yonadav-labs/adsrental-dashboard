from multiprocessing.pool import ThreadPool
from itertools import chain, islice

from django.db import connection
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
    result = lead.find_errors()
    connection.close()
    return result


class Command(BaseCommand):
    help = 'Troubleshoot EC2 instances to DB'

    def add_arguments(self, parser):
        parser.add_argument('--fix', action='store_true')
        parser.add_argument('--threads', type='int', default=10)
        parser.add_argument('--chunk-size', type='int', default=10)

    def handle(
        self,
        fix,
        threads,
        chunk_size,
        **kwargs
    ):
        leads = Lead.objects.filter(raspberry_pi__isnull=False, status__in=Lead.STATUSES_ACTIVE).order_by('-id')
        total = leads.count()
        counter = 0
        for lead_chunk in chunks(leads, chunk_size):
            pool = ThreadPool(processes=threads)
            lead_queue = [(i, fix) for i in lead_chunk]
            print 'Start pool: {} / {}'.format(counter, total)
            results = pool.map(troubleshoot, lead_queue)
            counter += len(lead_queue)
            print 'End pool: {} / {}'.format(counter, total)
            for result in results:
                print '\n'.join(result)
