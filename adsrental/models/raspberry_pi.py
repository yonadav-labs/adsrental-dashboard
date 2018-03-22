from __future__ import unicode_literals

import os
import datetime

from django.utils import timezone
from django.db import models
from django.conf import settings
from django_bulk_update.manager import BulkUpdateManager

from adsrental.models.raspberry_pi_session import RaspberryPiSession


class RaspberryPi(models.Model):
    """
    Stores a single RaspberryPi device entry, related to :model:`adsrental.Lead`. It does not have direct connection to
    :model:`adsrental.EC2Instance`, but it always can be obtained from related Lead.

    It is created automatically when you use *Mark as Qualified, Assign RPi, create Shipstation order* action in Lead admin.

    **How to test RaspberryPi device**

    It does not matter if it is inital testing or reshipment, actions are the same:

    1. Use *Prepare for testing* action for this lead. On this form you can specify extra RPIDs to prepare for testing. Paste any data to textarea
       and values like *RP<numbers>* will be prepared for testing as well. Make sure lead status is Qualified.
    2. Download latest firmware if you do not have it: `https://s3-us-west-2.amazonaws.com/mvp-store/pi_1.0.26.zip`
    3. Flash Firmware to SD card using Etcher `https://etcher.io/`
    4. Download `pi.conf` file for this device by clicking *Config file* link in admin for this lead
    5. Copy `pi.conf` to SD card root folder.If you are using MacOS/Linux you will see two partitions, use *boot* one.
    6. Safe eject SD card to prevent dataloss.
    7. Insert SD card to RaspberryPi device. If everything is okay, in 10 seconds RaspbeerPi green LED on device should start blinking.
    8. Device can reboot up to 2 times (partition table fix and update to latest patch), so give it at least 3 minutes.
    9. Check `Tested` mark in admin.
    10. Device is ready to be shipped to the end user

    If anything goes wrong, report to @Vlad in Slack.
    """

    online_minutes_ttl = 10
    first_tested_hours_ttl = 1
    last_offline_reported_hours_ttl = 2 * 24

    rpid = models.CharField(primary_key=True, max_length=255, unique=True)
    leadid = models.CharField(max_length=255, blank=True, null=True)
    first_seen = models.DateTimeField(blank=True, null=True)
    first_tested = models.DateTimeField(blank=True, null=True)
    ip_address = models.CharField(max_length=20, blank=True, null=True)
    last_seen = models.DateTimeField(blank=True, null=True, db_index=True)
    tunnel_last_tested = models.DateTimeField(blank=True, null=True)
    online_since_date = models.DateTimeField(blank=True, null=True)
    last_offline_reported = models.DateTimeField(blank=True, null=True, default=timezone.now)
    restart_required = models.BooleanField(default=False)
    version = models.CharField(max_length=20, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = BulkUpdateManager()

    @classmethod
    def get_free_or_create(cls):
        free_item = cls.objects.filter(lead__isnull=True, rpid__startswith='RP', first_seen__isnull=True).order_by('rpid').first()
        if free_item:
            return free_item

        return cls.create()

    @classmethod
    def create(cls):
        max_rpid = RaspberryPi.objects.filter(rpid__startswith='RP0').order_by('-rpid').first().rpid
        max_rpid_number = int(''.join([i for i in max_rpid if i.isdigit()]))
        next_rpid = 'RP%08d' % (max_rpid_number + 1)
        item = cls(rpid=next_rpid)
        item.save()
        return item

    def get_lead(self):
        'Get linked Lead object'
        try:
            return self.lead
        except RaspberryPi.lead.RelatedObjectDoesNotExist:
            return None

    def get_ec2_instance(self):
        lead = self.get_lead()
        if not lead:
            return None

        return lead.get_ec2_instance()

    def report_offline(self):
        self.last_offline_reported = timezone.now()
        if self.online_since_date:
            self.online_since_date = None

        self.save()
        RaspberryPiSession.end(self)

    def update_ping(self, now=None):
        if now is None:
            now = timezone.now()

        if not self.first_tested:
            self.first_tested = now
            lead = self.get_lead()
            if lead:
                lead.tested = True
                lead.save()
            return True

        if self.first_tested + datetime.timedelta(hours=self.first_tested_hours_ttl) > now:
            return False

        if self.online_since_date is None:
            self.online_since_date = now
            RaspberryPiSession.start(self)

        lead = self.get_lead()
        if lead and lead.status == lead.STATUS_QUALIFIED:
            lead.set_status(lead.STATUS_IN_PROGRESS, edited_by=None)
            lead.sync_to_adsdb()

        if not self.first_seen:
            self.first_seen = now
            self.last_seen = now
            return True

        self.last_seen = now
        return True

    def online(self):
        if self.last_seen is None:
            return False

        return (timezone.now() - self.get_last_seen()).total_seconds() < self.online_minutes_ttl * 60

    def get_first_seen(self):
        if self.first_seen is None:
            return None

        return self.first_seen

    def get_last_log(self, tail=1):
        log_dir = os.path.join(settings.RASPBERRY_PI_LOG_PATH, self.rpid)
        if not os.path.exists(log_dir):
            return ''

        log_files = os.listdir(log_dir)
        if not log_files:
            return ''

        last_log = sorted(log_files)[-1]
        last_log_path = os.path.join(log_dir, last_log)
        lines = open(last_log_path).readlines()[-tail:]
        return '\n'.join([i.rstrip('\n') for i in lines])

    def get_last_seen(self):
        if self.last_seen is None:
            return None

        return self.last_seen

    def __str__(self):
        return self.rpid

    @staticmethod
    def get_max_datetime(date1, date2):
        if not date1:
            return date2
        if not date2:
            return date1
        if date1 > date2:
            return date1

        return date2

    class Meta:
        db_table = 'raspberry_pi'
