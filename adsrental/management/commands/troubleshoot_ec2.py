from multiprocessing.pool import ThreadPool
from itertools import chain, islice

from django.core.management.base import BaseCommand

from adsrental.models.ec2_instance import EC2Instance


def chunks(iterable, size=10):
    iterator = iter(iterable)
    for first in iterator:
        yield chain([first], islice(iterator, size - 1))


class Command(BaseCommand):
    help = 'Troubleshoot EC2 instances to DB'
    threads_count = 10
    chunk_size = 50

    def add_arguments(self, parser):
        parser.add_argument('--fix', action='store_true')

    def handle(
        self,
        fix,
        **kwargs
    ):
        instances = EC2Instance.objects.all().order_by('-id')
        for instance_chunk in chunks(instances, self.chunk_size):
            pool = ThreadPool(processes=self.threads_count)
            instance_queue = [(i, fix) for i in instance_chunk]
            print 'Start pool'
            res = pool.map(EC2Instance.cls_troubleshoot, instance_queue)
            print 'End pool'
            for result in res:
                print res
