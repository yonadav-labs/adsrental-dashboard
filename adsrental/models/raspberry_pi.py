from __future__ import unicode_literals

import os
import datetime

from django.utils import timezone
from django.db import models
from django.conf import settings

from adsrental.models.raspberry_pi_session import RaspberryPiSession


class RaspberryPi(models.Model):
    online_hours_ttl = 6
    first_tested_hours_ttl = 1
    tunnel_online_hours_ttl = 1
    last_offline_reported_hours_ttl = 2 * 24

    rpid = models.CharField(primary_key=True, max_length=255, unique=True)
    leadid = models.CharField(max_length=255, blank=True, null=True)
    ipaddress = models.CharField(max_length=255, blank=True, null=True)
    ec2_hostname = models.CharField(max_length=255, blank=True, null=True)
    first_seen = models.DateTimeField(blank=True, null=True)
    first_tested = models.DateTimeField(blank=True, null=True)
    last_seen = models.DateTimeField(blank=True, null=True, db_index=True)
    tunnel_last_tested = models.DateTimeField(blank=True, null=True)
    online_since_date = models.DateTimeField(blank=True, null=True)
    last_offline_reported = models.DateTimeField(blank=True, null=True, default=timezone.now)
    restart_required = models.BooleanField(default=False)
    version = models.CharField(max_length=20, default=settings.IMAGE_RASPBERRY_PI_VERSION)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

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
        try:
            return self.lead
        except:
            pass

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

    def update_ping(self):
        now = timezone.now()

        if not self.first_tested:
            self.first_tested = now
            if self.lead:
                self.lead.tested = True
                self.lead.save()
            return True

        if self.first_tested + datetime.timedelta(hours=self.first_tested_hours_ttl) > now:
            return False

        if self.online_since_date is None:
            self.online_since_date = now
            RaspberryPiSession.start(self)

        lead = self.get_lead()
        if lead and lead.status == lead.STATUS_QUALIFIED:
            lead.set_status(lead.STATUS_IN_PROGRESS, edited_by=None)

        if not self.first_seen:
            self.first_seen = now
            self.last_seen = now
            return True

        self.last_seen = now
        return True

    def online(self):
        if self.last_seen is None:
            return False

        return (timezone.now() - self.get_last_seen()).total_seconds() < self.online_hours_ttl * 60 * 60

    def tunnel_online(self):
        if self.tunnel_last_tested is None:
            return False

        return (timezone.now() - self.get_tunnel_last_tested()).total_seconds() < self.tunnel_online_hours_ttl * 60 * 60

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
        return '\n'.join(lines)

    def get_last_seen(self):
        if self.last_seen is None:
            return None

        return self.last_seen

    def get_tunnel_last_tested(self):
        if self.tunnel_last_tested is None:
            return None

        return self.tunnel_last_tested

    def __str__(self):
        return self.rpid

    @staticmethod
    def get_max_datetime(a, b):
        if not a:
            return b
        if not b:
            return a
        if a > b:
            return a

        return b

    class Meta:
        db_table = 'raspberry_pi'
