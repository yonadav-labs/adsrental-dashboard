from __future__ import unicode_literals

import os
import csv

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from adsrental.models import RaspberryPi, EC2Instance, Lead, BrowserExtension


class Command(BaseCommand):
    help = 'Load data from SalesForce dumps'

    def add_arguments(self, parser):
        parser.add_argument('dir')
        parser.add_argument('load', nargs='+', choices=['ec2', 'ext', 'lead', 'rpi'], default=[])

    def handle(self, *args, **options):
        dump_dir = os.path.join(settings.BASE_DIR, 'sf_dump', options['dir'])
        print 'Reading dumps from {}'.format(dump_dir)
        if not os.path.exists(dump_dir):
            raise CommandError('Dump does not exist')

        if 'ec2' in options['load']:
            print 'Reading ec2.csv'
            with open(os.path.join(dump_dir, 'ec2.csv'), 'rb') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    print 'Importing EC2Instance {}'.format(row['NAME'])
                    EC2Instance.upsert_from_sf(row)

        if 'rpi' in options['load']:
            print 'Reading rpi.csv'
            with open(os.path.join(dump_dir, 'rpi.csv'), 'rb') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    print 'Importing RaspberryPI {}'.format(row['NAME'])
                    RaspberryPi.upsert_from_sf(row)

        if 'lead' in options['load']:
            print 'Reading lead.csv'
            with open(os.path.join(dump_dir, 'lead.csv'), 'rb') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    print 'Importing Lead {}'.format(row['NAME'])
                    Lead.upsert_from_sf(row)

        if 'ext' in options['load']:
            print 'Reading extension.csv'
            with open(os.path.join(dump_dir, 'extension.csv'), 'rb') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    print 'Importing BrowserExtension {}'.format(row['NAME'])
                    BrowserExtension.upsert_from_sf(row)
