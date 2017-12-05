from __future__ import unicode_literals

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
    google_account = models.IntegerField()
    facebook_account = models.IntegerField()
    raspberry_pi = models.ForeignKey('adsrental.RaspberryPi', null=True, blank=True)

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

    class Meta:
        db_table = 'raspberry_pi'
