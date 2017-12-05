from __future__ import unicode_literals

from django.utils import timezone
from django.db import models


class Lead(models.Model):
    leadid = models.CharField(primary_key=True, max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    account_name = models.CharField(max_length=255)
    usps_tracking_code = models.CharField(max_length=255, blank=True, null=True)
    utm_source = models.CharField(max_length=80, blank=True, null=True)
    google_account = models.BooleanField(default=False)
    facebook_account = models.BooleanField(default=False)
    raspberry_pi = models.ForeignKey('adsrental.RaspberryPi', null=True, blank=True)
    wrong_password = models.BooleanField(default=False)
    bundler_paid = models.BooleanField(default=False)
    pi_delivered = models.BooleanField(default=False)

    def __str__(self):
        return self.leadid

    class Meta:
        db_table = 'lead'


class RaspberryPi(models.Model):
    rpid = models.CharField(primary_key=True, max_length=255)
    leadid = models.CharField(max_length=255, blank=True, null=True)
    ipaddress = models.CharField(max_length=255)
    ec2_hostname = models.CharField(max_length=255, blank=True, null=True)
    first_seen = models.DateTimeField()
    last_seen = models.DateTimeField()
    tunnel_last_tested = models.DateTimeField(blank=True, null=True)

    def online(self):
        if self.last_seen is None:
            return False

        return (timezone.now() - self.last_seen).total_seconds() < 7 * 60 * 60

    def tunnel_online(self):
        if self.tunnel_last_tested is None:
            return False

        return (timezone.now() - self.tunnel_last_tested).total_seconds() < 7 * 60 * 60

    def __str__(self):
        return self.rpid

    class Meta:
        db_table = 'raspberry_pi'
