from __future__ import annotations

import re
import os
import datetime
import typing
import random

import requests
from django.utils import timezone
from django.db import models
from django.db.models import Count
from django.conf import settings
from django_bulk_update.manager import BulkUpdateManager

from adsrental.models.raspberry_pi_session import RaspberryPiSession
from adsrental.utils import PingCacheHelper
from adsrental.models.user import User


if typing.TYPE_CHECKING:
    from adsrental.models.lead import Lead
    from adsrental.models.ec2_instance import EC2Instance


PingDataType = typing.Dict


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
    first_tested_hours_ttl = 12
    last_offline_reported_hours_ttl = 2 * 24

    TUNNEL_HOST = '178.128.1.68'
    TUNNEL_USER = 'proxykeeper'
    TUNNEL_PASSWORD = 'keepitsecret'
    TUNNEL_PORT_START = 20000
    TUNNEL_PORT_END = 65000

    PROXY_HOSTNAME_CHOICES = (
        ('178.128.1.68', 'Proxykeeper', ),
        ('138.197.219.240', 'Proxykeeper2', ),
        ('138.197.197.65', 'Proxykeeper3', ),
        ('157.230.146.152', 'Proxykeeper4', ),
        ('157.230.155.97', 'Proxykeeper5', ),
        ('134.209.52.3', 'Proxykeeper6', ),
        ('68.183.163.172', 'Proxykeeper7', ),
    )

    # lead = models.OneToOneField('adsrental.Lead', blank=True, null=True, help_text='Corresponding lead', on_delete=models.SET_NULL, related_name='raspberry_pis', related_query_name='raspberry_pi')
    rpid = models.CharField(primary_key=True, max_length=255, unique=True)
    rpid_numeric = models.PositiveIntegerField(null=True, blank=True)
    leadid = models.CharField(max_length=255, blank=True, null=True)
    first_seen = models.DateTimeField(blank=True, null=True)
    first_tested = models.DateTimeField(blank=True, null=True)
    ip_address = models.CharField(max_length=20, blank=True, null=True)
    last_seen = models.DateTimeField(blank=True, null=True, db_index=True)
    tunnel_last_tested = models.DateTimeField(blank=True, null=True)
    online_since_date = models.DateTimeField(blank=True, null=True)
    last_offline_reported = models.DateTimeField(blank=True, null=True, default=timezone.now)
    is_proxy_tunnel = models.BooleanField(default=False, help_text='If True - RPi works as an HTTP proxy')
    is_beta = models.BooleanField(default=False, help_text='If True - RPi gets beta firmwares')
    tunnel_port = models.PositiveIntegerField(null=True, blank=True, unique=True, help_text='Port to create a tunnel to proxykeeper')
    rtunnel_port = models.PositiveIntegerField(null=True, blank=True, unique=True, help_text='Port to create a reverse tunnel from proxykeeper')
    proxy_hostname = models.CharField(choices=PROXY_HOSTNAME_CHOICES, max_length=50, default=TUNNEL_HOST, help_text='Hostname tunnel to proxykeeper')
    proxy_password = models.CharField(max_length=50, default=TUNNEL_PASSWORD, help_text='Hostname password for proxykeeper user')
    proxy_delay = models.FloatField(null=True, blank=True, default=None, help_text='Proxy response from tunnel')
    proxy_delay_datetime = models.DateTimeField(blank=True, null=True, help_text='Date of tunnel last check')
    restart_required = models.BooleanField(default=False)
    new_config_required = models.BooleanField(default=False)
    version = models.CharField(max_length=20, blank=True, null=True)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)

    objects = BulkUpdateManager()

    @classmethod
    def get_free_or_create(cls) -> RaspberryPi:
        free_item = cls.objects.filter(lead__isnull=True, rpid__startswith='RP', first_seen__isnull=True).order_by('rpid').first()
        if free_item:
            return free_item

        return cls.create_with_rpid()

    @classmethod
    def create_with_rpid(cls) -> RaspberryPi:
        next_rpid_numeric = 1
        last_rpi = RaspberryPi.objects.filter(rpid_numeric__isnull=False).order_by('-created').first()
        if last_rpi:
            next_rpid_numeric = last_rpi.rpid_numeric + 1

        next_rpid = 'RP%08d' % next_rpid_numeric
        item = cls(
            rpid=next_rpid,
            rpid_numeric=next_rpid_numeric,
        )
        item.save()
        item.is_proxy_tunnel = True
        item.assign_proxy_hostname()
        item.assign_tunnel_ports()
        item.save()
        return item

    def get_lead(self) -> typing.Optional[Lead]:
        'Get linked Lead object'
        try:
            return self.lead  # pylint: disable=E1101
        except RaspberryPi.lead.RelatedObjectDoesNotExist:  # pylint: disable=E1101
            return None

    def get_proxy_delay(self) -> float:
        try:
            response = self.check_proxy_tunnel()
        except requests.ConnectionError:
            return 999.0
        except requests.exceptions.RequestException:
            return 899.0

        return response.elapsed.total_seconds()

    def get_ec2_instance(self) -> typing.Optional[EC2Instance]:
        lead = self.get_lead()
        if not lead:
            return None

        return lead.get_ec2_instance()

    def find_tunnel_ports(self) -> typing.Tuple[int, int]:
        tunnel_ports = [i[0] for i in RaspberryPi.objects.filter(tunnel_port__isnull=False).values_list('tunnel_port')]
        tunnel_port = random.randint(RaspberryPi.TUNNEL_PORT_START, RaspberryPi.TUNNEL_PORT_END) // 2 * 2
        while tunnel_port in tunnel_ports:
            tunnel_port = random.randint(RaspberryPi.TUNNEL_PORT_START, RaspberryPi.TUNNEL_PORT_END) // 2 * 2

        return (tunnel_port, tunnel_port + 1)

    def assign_proxy_hostname(self) -> str:
        hostname_count = RaspberryPi.objects.filter(lead__status='In-Progress', is_proxy_tunnel=True).exclude(proxy_hostname='').values('proxy_hostname').annotate(count=Count('rpid')).order_by('count')

        hostnames = []
        for i in hostname_count:
            hostnames.append(i['proxy_hostname'])

        for proxy_hostname, _ in RaspberryPi.PROXY_HOSTNAME_CHOICES:
            if proxy_hostname not in hostnames:
                self.proxy_hostname = proxy_hostname
                return self.proxy_hostname

        self.proxy_hostname = hostname_count.first()['proxy_hostname']
        return self.proxy_hostname

    def assign_tunnel_ports(self) -> None:
        self.tunnel_port, self.rtunnel_port = self.find_tunnel_ports()

    def unassign_tunnel_ports(self) -> None:
        self.tunnel_port, self.rtunnel_port = None, None

    def is_in_testing(self) -> bool:
        if self.first_seen:
            return False
        if not self.first_tested:
            return False

        return True

    def report_offline(self) -> None:
        now = timezone.localtime(timezone.now())
        self.last_offline_reported = now
        if self.online_since_date:
            self.online_since_date = None

        self.save()
        RaspberryPiSession.end(self)

    def _update_ping(self, ping_datetime: datetime.datetime) -> bool:
        if not self.first_tested:
            self.first_tested = ping_datetime
            lead = self.get_lead()
            return True

        if self.first_tested + datetime.timedelta(hours=self.first_tested_hours_ttl) > ping_datetime:
            return False

        if self.online_since_date is None:
            self.online_since_date = ping_datetime
            RaspberryPiSession.start(self)

        lead = self.get_lead()
        ping_user = User.objects.get(email=settings.PING_USER_EMAIL)
        if lead:
            if lead.status == lead.STATUS_QUALIFIED:
                lead.set_status(lead.STATUS_IN_PROGRESS, edited_by=ping_user)
                lead.save()
            for lead_account in lead.lead_accounts.filter(status='Qualified'):
                if lead_account.is_approval_needed():
                    lead_account.set_status(lead_account.STATUS_NEEDS_APPROVAL, edited_by=ping_user)
                    lead_account.save()
                    lead.set_status(lead.STATUS_NEEDS_APPROVAL, edited_by=ping_user)
                    lead.save()
                    continue

                lead_account.set_status(lead_account.STATUS_IN_PROGRESS, edited_by=ping_user)
                if not lead_account.in_progress_date:
                    lead_account.in_progress_date = ping_datetime
                    lead_account.add_comment('Set to in-progress after first ping', ping_user)
                    # lead_account.insert_note('Set to in-progress after first ping')
                    # lead_account.save()

        if not self.first_seen:
            self.first_seen = ping_datetime
            self.last_seen = ping_datetime
            return True

        self.last_seen = ping_datetime
        return True

    def online(self) -> bool:
        last_seen = self.get_last_seen()
        if last_seen is None:
            return False

        return (timezone.now() - last_seen).total_seconds() < self.online_minutes_ttl * 60

    @classmethod
    def get_objects_online(cls) -> models.query.QuerySet:
        now = timezone.localtime(timezone.now())
        if settings.LOCAL:
            now = now - datetime.timedelta(days=180)
        return cls.objects.filter(last_seen__gte=now - datetime.timedelta(minutes=cls.online_minutes_ttl))

    @classmethod
    def get_objects_offline(cls) -> models.query.QuerySet:
        now = timezone.localtime(timezone.now())
        return cls.objects.all().exclude(last_seen__gte=now - datetime.timedelta(minutes=cls.online_minutes_ttl))

    @classmethod
    def get_last_seen_online_dt(cls, now=None) -> datetime.datetime:
        if not now:
            now = timezone.now()
        if settings.LOCAL:
            return now - datetime.timedelta(days=180)
        return now - datetime.timedelta(minutes=cls.online_minutes_ttl)

    def get_first_seen(self) -> typing.Optional[datetime.datetime]:
        if self.first_seen is None:
            return None

        return self.first_seen

    def get_last_log(self, tail: int = 1) -> str:
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

    def get_last_seen(self) -> typing.Optional[datetime.datetime]:
        if self.last_seen is None or self.first_seen is None:
            return None

        return self.last_seen

    def __str__(self) -> str:
        return self.rpid

    @staticmethod
    def get_max_datetime(date1: typing.Optional[datetime.datetime], date2: typing.Optional[datetime.datetime]) -> typing.Optional[datetime.datetime]:
        if not date1:
            return date2
        if not date2:
            return date1
        if date1 > date2:
            return date1

        return date2

    def reset_cache(self) -> None:
        ping_cache_helper = PingCacheHelper()
        ping_data = ping_cache_helper.get(self.rpid)

        if ping_data:
            self.process_ping_data(ping_data)
            self.save()
            ping_cache_helper.delete(self.rpid)

    def get_cache(self) -> typing.Optional[PingDataType]:
        ping_cache_helper = PingCacheHelper()
        ping_data = ping_cache_helper.get(self.rpid)
        return ping_data

    def process_ping_data(self, ping_data: PingDataType) -> None:
        ip_address = ping_data['ip_address']
        version = ping_data['raspberry_pi_version']
        last_ping = ping_data.get('last_ping') or timezone.localtime(timezone.now())

        lead = self.get_lead()
        if lead and lead.is_active():
            self._update_ping(last_ping)

        if self.ip_address != ip_address:
            self.ip_address = ip_address
        if version and self.version != version:
            self.version = version

        self.restart_required = False
        self.new_config_required = False
        self.version = version

    def get_proxy_connection_string(self) -> str:
        return f'socks5://{self.TUNNEL_USER}:{self.TUNNEL_PASSWORD}@{self.proxy_hostname}:{self.rtunnel_port}'

    def check_proxy_tunnel(self) -> requests.Response:
        return requests.get(
            'https://google.com',
            proxies=dict(
                http=self.get_proxy_connection_string(),
                https=self.get_proxy_connection_string(),
            ),
            timeout=5,
        )

    def reassign_proxy(self) -> None:
        self.reset_cache()
        self.assign_proxy_hostname()
        self.assign_tunnel_ports()
        self.new_config_required = True
        self.proxy_delay = None
        self.proxy_delay_datetime = None

    def get_unique_ips(self) -> typing.List[str]:
        last_log = self.get_last_log(tail=1000)
        ips = list(set(re.findall(r'\d+\.\d+\.\d+\.\d+', last_log)))
        ips = [i for i in ips if i != self.proxy_hostname]
        return ips

    class Meta:
        db_table = 'raspberry_pi'
