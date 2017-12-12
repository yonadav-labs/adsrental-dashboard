from __future__ import unicode_literals

import datetime

from django.utils import timezone
from django.db import models

from salesforce_handler.models import RaspberryPi as SFRaspberryPi


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
