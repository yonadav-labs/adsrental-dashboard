from multiprocessing.pool import ThreadPool
import datetime
import logging
import argparse
from typing import Tuple, Text

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.db.models import Q

from adsrental.models.raspberry_pi import RaspberryPi


def proxykeeper_ip(proxykeeper: Text) -> Text:
    for ip, name in RaspberryPi.PROXY_HOSTNAME_CHOICES:
        if proxykeeper.lower() == name.lower():
            return ip

    raise argparse.ArgumentTypeError(f'Unknown proxykeeper name: {proxykeeper}')


class Command(BaseCommand):
    help = 'Revive old EC2 EC2'
    force = False

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        formatter = logging.Formatter('%(asctime)-15s %(message)s')
        logging.raiseExceptions = False
        logger = logging.Logger('update_proxy_delay')
        logger.setLevel(logging.INFO)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        self.logger = logger

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--min-delay', type=int, default=0)
        parser.add_argument('--threads', type=int, default=10)
        parser.add_argument('--limit', type=int, default=100)
        parser.add_argument('-p', '--proxykeeper', type=proxykeeper_ip, nargs='*', default=[])
        parser.add_argument('--fix', action='store_true')

    def runner(self, raspberry_pi: RaspberryPi) -> Tuple[RaspberryPi, float, datetime.datetime]:
        now = timezone.localtime(timezone.now())
        old_proxy_delay = raspberry_pi.proxy_delay
        old_proxy_delay_str = f'{round(old_proxy_delay, 2)}s' if old_proxy_delay else 'n/a'
        proxy_delay = raspberry_pi.get_proxy_delay()
        self.logger.info(f'{raspberry_pi} - {old_proxy_delay_str} -> {round(proxy_delay, 2)}s on {raspberry_pi.get_proxy_hostname_display()}')
        return (raspberry_pi, proxy_delay, now)

    def handle(self, *args: str, **options: str) -> None:
        min_delay = int(options['min_delay'])
        threads = int(options['threads'])
        limit = int(options['limit'])
        fix_dead = bool(options['fix'])
        proxykeeper_ips = options['proxykeeper']
        raspberry_pis = RaspberryPi.get_objects_online().filter(is_proxy_tunnel=True)
        raspberry_pis = raspberry_pis.filter(Q(proxy_delay__gte=min_delay) | Q(proxy_delay__isnull=True))

        if proxykeeper_ips:
            raspberry_pis = raspberry_pis.filter(proxy_hostname__in=proxykeeper_ips)

        raspberry_pis = raspberry_pis.order_by('proxy_delay_datetime')

        raspberry_pis_limited = raspberry_pis[: limit]
        self.logger.info(f'Total {raspberry_pis.count()}, limited to {raspberry_pis_limited.count()}')

        pool = ThreadPool(processes=threads)
        results = pool.map(self.runner, raspberry_pis_limited)
        self.logger.info(f'Upserting results...')
        for raspberry_pi, proxy_delay, check_date in results:
            raspberry_pi.proxy_delay = proxy_delay
            raspberry_pi.proxy_delay_datetime = check_date
            if fix_dead and proxy_delay > 800.0:
                raspberry_pi.reassign_proxy()
                self.logger.info(f'{raspberry_pi} switched to {raspberry_pi.get_proxy_hostname_display()}')

            raspberry_pi.save()
        self.logger.info(f'Done')
