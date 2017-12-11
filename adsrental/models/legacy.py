from __future__ import unicode_literals

import datetime

from django.utils import timezone
from django.db import models
# from salesforce_handler.models import Lead as SFLead
from salesforce_handler.models import RaspberryPi as SFRaspberryPi


class Lead(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Banned', 'Banned'),
        ('Qualified', 'Qualified'),
        ('In-Progress', 'In-Progress'),
    ]

    leadid = models.CharField(primary_key=True, max_length=255)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='Available')
    email = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    account_name = models.CharField(max_length=255, blank=True, null=True)
    usps_tracking_code = models.CharField(max_length=255, blank=True, null=True)
    utm_source = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    google_account = models.BooleanField(default=False)
    facebook_account = models.BooleanField(default=False)
    raspberry_pi = models.ForeignKey('adsrental.RaspberryPi', null=True, blank=True)
    wrong_password = models.BooleanField(default=False)
    bundler_paid = models.BooleanField(default=False)
    pi_delivered = models.BooleanField(default=False)
    facebook_account_status = models.CharField(max_length=255, choices=[('Available', 'Available'), ('Banned', 'Banned')], blank=True, null=True)
    google_account_status = models.CharField(max_length=255, choices=[('Available', 'Available'), ('Banned', 'Banned')], blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    pi_sent = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.leadid

    class Meta:
        db_table = 'lead'

    def get_pi_sent_this_month(self):
        if not self.pi_sent:
            return False
        now = timezone.now()
        if now.year == self.pi_sent.year and now.month == self.pi_sent.month:
            return True

        return False

    @staticmethod
    def upsert_from_sf(sf_lead):
        raspberry_pi = None
        if sf_lead.raspberry_pi:
            raspberry_pi = RaspberryPi.upsert_from_sf(sf_lead.id, sf_lead.raspberry_pi)

        lead = Lead.objects.filter(leadid=sf_lead.id).first()
        if lead is None:
            lead = Lead(
                leadid=sf_lead.id,
            )

        lead.first_name = sf_lead.first_name
        lead.last_name = sf_lead.last_name
        lead.email = sf_lead.email
        lead.phone = sf_lead.phone
        lead.address = ', '.join([
            sf_lead.street or '',
            sf_lead.city or '',
            sf_lead.state or '',
            sf_lead.postal_code or '',
            sf_lead.country or '',
        ])
        lead.account_name = sf_lead.account_name
        lead.status = sf_lead.status
        lead.usps_tracking_code = sf_lead.raspberry_pi.usps_tracking_code if sf_lead.raspberry_pi else None
        lead.utm_source = sf_lead.utm_source
        lead.google_account = sf_lead.google_account
        lead.facebook_account = sf_lead.facebook_account
        lead.raspberry_pi = raspberry_pi
        lead.wrong_password = sf_lead.wrong_password
        lead.bundler_paid = sf_lead.bundler_paid
        lead.pi_delivered = sf_lead.raspberry_pi.delivered if sf_lead.raspberry_pi else False
        lead.facebook_account_status = sf_lead.facebook_account_status
        lead.google_account_status = sf_lead.google_account_status
        lead.save()
        return lead

    @staticmethod
    def upsert_to_sf(leads):
        pass


class RaspberryPi(models.Model):
    rpid = models.CharField(primary_key=True, max_length=255)
    leadid = models.CharField(max_length=255, blank=True, null=True)
    ipaddress = models.CharField(max_length=255, blank=True, null=True)
    ec2_hostname = models.CharField(max_length=255, blank=True, null=True)
    first_seen = models.DateTimeField(blank=True, null=True)
    last_seen = models.DateTimeField(blank=True, null=True)
    tunnel_last_tested = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def online(self):
        if self.last_seen is None:
            return False

        return (timezone.now() - self.get_last_seen()).total_seconds() < 7 * 60 * 60

    def tunnel_online(self):
        if self.tunnel_last_tested is None:
            return False

        return (timezone.now() - self.get_tunnel_last_tested()).total_seconds() < 7 * 60 * 60

    def get_first_seen(self):
        if self.first_seen is None:
            return None

        return self.first_seen + datetime.timedelta(hours=7)

    def get_last_seen(self):
        if self.last_seen is None:
            return None

        return self.last_seen + datetime.timedelta(hours=7)

    def get_tunnel_last_tested(self):
        if self.tunnel_last_tested is None:
            return None

        return self.tunnel_last_tested + datetime.timedelta(hours=7)

    def __str__(self):
        return self.rpid

    @staticmethod
    def upsert_from_sf(lead_id, sf_raspberry_pi):
        raspberry_pi = RaspberryPi.objects.filter(rpid=sf_raspberry_pi.name).first()
        if raspberry_pi is None:
            raspberry_pi = RaspberryPi(
                rpid=sf_raspberry_pi.name,
                leadid=lead_id,
                ipaddress=sf_raspberry_pi.current_ip_address,
            )

        raspberry_pi.leadid = lead_id
        raspberry_pi.ipaddress = sf_raspberry_pi.current_ip_address
        # raspberry_pi.ec2_hostname = sf_raspberry_pi.ec2
        if sf_raspberry_pi.first_seen is not None:
            if raspberry_pi.first_seen is None or sf_raspberry_pi.first_seen > raspberry_pi.first_seen:
                raspberry_pi.first_seen = sf_raspberry_pi.first_seen
        if sf_raspberry_pi.last_seen is not None:
            if raspberry_pi.last_seen is None or sf_raspberry_pi.last_seen > raspberry_pi.last_seen:
                raspberry_pi.last_seen = sf_raspberry_pi.last_seen
        if sf_raspberry_pi.tunnel_last_tested is not None:
            if raspberry_pi.tunnel_last_tested is None or sf_raspberry_pi.tunnel_last_tested > raspberry_pi.tunnel_last_tested:
                raspberry_pi.tunnel_last_tested = sf_raspberry_pi.tunnel_last_tested
        raspberry_pi.save()
        return raspberry_pi

    @staticmethod
    def upsert_to_sf(raspberry_pis):
        names = []
        names_map = {}
        for r in raspberry_pis:
            names.append(r.rpid)
            names_map[r.rpid] = r

        sf_raspberry_pis = SFRaspberryPi.objects.filter(name__in=names)
        for sf_raspberry_pi in sf_raspberry_pis:
            sf_raspberry_pi.first_seen = names_map[sf_raspberry_pi.name].first_seen
            sf_raspberry_pi.last_seen = names_map[sf_raspberry_pi.name].last_seen
            sf_raspberry_pi.tunnel_last_tested = names_map[sf_raspberry_pi.name].tunnel_last_tested
            sf_raspberry_pi.current_ip_address = names_map[sf_raspberry_pi.name].ipaddress
            sf_raspberry_pi.save()

    class Meta:
        db_table = 'raspberry_pi'
