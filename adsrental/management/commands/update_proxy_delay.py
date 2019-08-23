from multiprocessing.pool import ThreadPool
import datetime
import logging
import argparse
from typing import Tuple

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

from adsrental.models.raspberry_pi import RaspberryPi


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
        parser.add_argument('--set', action='store_true')
        parser.add_argument('--threads', type=int, default=10)
        parser.add_argument('--limit', type=int, default=100)

    def runner(self, raspberry_pi: RaspberryPi) -> Tuple[RaspberryPi, float, datetime.datetime]:
        now = timezone.localtime(timezone.now())
        old_proxy_delay = raspberry_pi.proxy_delay
        old_proxy_delay_str = f'{round(old_proxy_delay, 2)}s' if old_proxy_delay else 'n/a'
        proxy_delay = raspberry_pi.get_proxy_delay()
        self.logger.info(f'{raspberry_pi} - {old_proxy_delay_str} -> {round(proxy_delay, 2)}s on {raspberry_pi.get_proxy_hostname_display()}')
        return (raspberry_pi, proxy_delay, now)

    def handle(self, *args: str, **options: str) -> None:
        update_set = bool(options['set'])
        threads = int(options['threads'])
        limit = int(options['limit'])
        raspberry_pis = RaspberryPi.get_objects_online()

        if not update_set:
            raspberry_pis = raspberry_pis.filter(proxy_delay__isnull=True)
        raspberry_pis = raspberry_pis.order_by('proxy_delay_datetime')
        raspberry_pis_limited = raspberry_pis[:limit]
        self.logger.info(f'Total {raspberry_pis.count()}, limited to {raspberry_pis_limited.count()}')

        pool = ThreadPool(processes=threads)
        results = pool.map(self.runner, raspberry_pis_limited)
        self.logger.info(f'Upserting results...')
        for raspberry_pi, proxy_delay, check_date in results:
            raspberry_pi.proxy_delay = proxy_delay
            raspberry_pi.proxy_delay_datetime = check_date
            raspberry_pi.save()
        self.logger.info(f'Done')
