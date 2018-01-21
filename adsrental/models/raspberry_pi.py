from __future__ import unicode_literals

import datetime

from django.utils import timezone
from django.db import models
from django.apps import apps
from django.conf import settings


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
    last_offline_reported = models.DateTimeField(blank=True, null=True, default=timezone.now)
    restart_required = models.BooleanField(default=False)
    version = models.CharField(max_length=20, default='1.0.0')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

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

    @classmethod
    def upsert_from_sf(cls, sf_raspberry_pi, raspberry_pi):
        if raspberry_pi is None:
            raspberry_pi = RaspberryPi(
                rpid=sf_raspberry_pi.name,
                leadid=sf_raspberry_pi.linked_lead_id,
                ipaddress=sf_raspberry_pi.current_ip_address,
            )
            raspberry_pi.save()

        first_seen = cls.get_max_datetime(raspberry_pi.first_seen, sf_raspberry_pi.first_seen)
        last_seen = cls.get_max_datetime(raspberry_pi.last_seen, sf_raspberry_pi.last_seen)
        tunnel_last_tested = cls.get_max_datetime(raspberry_pi.tunnel_last_tested, sf_raspberry_pi.tunnel_last_tested)

        for new_field, old_field in (
            (sf_raspberry_pi.linked_lead_id, raspberry_pi.leadid, ),
            (sf_raspberry_pi.current_ip_address, raspberry_pi.ipaddress, ),
            (first_seen, raspberry_pi.first_seen, ),
            (last_seen, raspberry_pi.last_seen, ),
            (tunnel_last_tested, raspberry_pi.tunnel_last_tested, ),
        ):
            if new_field != old_field:
                break
        else:
            return raspberry_pi

        raspberry_pi.leadid = sf_raspberry_pi.linked_lead_id
        raspberry_pi.ipaddress = sf_raspberry_pi.current_ip_address
        # raspberry_pi.ec2_hostname = sf_raspberry_pi.ec2
        raspberry_pi.first_seen = first_seen
        raspberry_pi.last_seen = last_seen
        raspberry_pi.tunnel_last_tested = tunnel_last_tested

        raspberry_pi.save()
        return raspberry_pi

    @classmethod
    def upsert_to_sf(cls, sf_raspberry_pi, raspberry_pi):
        first_seen = cls.get_max_datetime(raspberry_pi.first_seen, sf_raspberry_pi.first_seen)
        last_seen = cls.get_max_datetime(raspberry_pi.last_seen, sf_raspberry_pi.last_seen)
        tunnel_last_tested = cls.get_max_datetime(raspberry_pi.tunnel_last_tested, sf_raspberry_pi.tunnel_last_tested)

        for new_field, old_field in (
            (sf_raspberry_pi.linked_lead_id, raspberry_pi.leadid, ),
            (sf_raspberry_pi.current_ip_address, raspberry_pi.ipaddress, ),
            (sf_raspberry_pi.first_seen, first_seen, ),
            (sf_raspberry_pi.last_seen, last_seen, ),
            (sf_raspberry_pi.tunnel_last_tested, tunnel_last_tested, ),
        ):
            if new_field != old_field:
                break
        else:
            return raspberry_pi

        sf_raspberry_pi.linked_lead_id = raspberry_pi.leadid
        sf_raspberry_pi.first_seen = first_seen
        sf_raspberry_pi.last_seen = last_seen
        sf_raspberry_pi.tunnel_last_tested = tunnel_last_tested
        sf_raspberry_pi.current_ip_address = raspberry_pi.ipaddress
        sf_raspberry_pi.last_modified_by_id = settings.SALESFORCE_API_USER_ID
        sf_raspberry_pi.save()

    def get_lead(self):
        Lead = apps.get_app_config('adsrental').get_model('Lead')
        return Lead.objects.filter(leadid=self.leadid).first()

    class Meta:
        db_table = 'raspberry_pi'
