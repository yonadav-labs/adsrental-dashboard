import os
import datetime

from django.utils import timezone
from django.db import models
from django.db.models import Count
from django.conf import settings
from django_bulk_update.manager import BulkUpdateManager

from adsrental.models.raspberry_pi_session import RaspberryPiSession
from adsrental.utils import PingCacheHelper


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
    restart_required = models.BooleanField(default=False)
    new_config_required = models.BooleanField(default=False)
    version = models.CharField(max_length=20, blank=True, null=True)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)

    objects = BulkUpdateManager()

    @classmethod
    def get_free_or_create(cls):
        free_item = cls.objects.filter(lead__isnull=True, rpid__startswith='RP', first_seen__isnull=True).order_by('rpid').first()
        if free_item:
            return free_item

        return cls.create_with_rpid()

    @classmethod
    def create_with_rpid(cls):
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

    def get_lead(self):
        'Get linked Lead object'
        try:
            return self.lead # pylint: disable=E1101
        except RaspberryPi.lead.RelatedObjectDoesNotExist: # pylint: disable=E1101
            return None

    def get_ec2_instance(self):
        lead = self.get_lead()
        if not lead:
            return None

        return lead.get_ec2_instance()

    def find_tunnel_ports(self):
        tunnel_ports = [i[0] for i in RaspberryPi.objects.filter(tunnel_port__isnull=False).exclude(rpid=self.rpid).values_list('tunnel_port')]
        for check_tunnel_port in range(RaspberryPi.TUNNEL_PORT_START, RaspberryPi.TUNNEL_PORT_END, 2):
            if check_tunnel_port in tunnel_ports:
                continue
            return (check_tunnel_port, check_tunnel_port + 1)

        raise ValueError('No free port found')

    def assign_proxy_hostname(self):
        hostname_count = RaspberryPi.get_objects_online().filter(is_proxy_tunnel=True).values('proxy_hostname').annotate(count=Count('rpid')).order_by('count')
        if not hostname_count:
            self.proxy_hostname = RaspberryPi.TUNNEL_HOST
            return

        self.proxy_hostname = hostname_count.first()['proxy_hostname']
        return

    def assign_tunnel_ports(self):
        self.tunnel_port, self.rtunnel_port = self.find_tunnel_ports()

    def unassign_tunnel_ports(self):
        self.tunnel_port, self.rtunnel_port = None, None

    def is_in_testing(self):
        if self.first_seen:
            return False
        if not self.first_tested:
            return False

        return True

    def report_offline(self):
        now = timezone.localtime(timezone.now())
        self.last_offline_reported = now
        if self.online_since_date:
            self.online_since_date = None

        self.save()
        RaspberryPiSession.end(self)

    def update_ping(self, now=None):
        if now is None:
            now = timezone.localtime(timezone.now())

        if not self.first_tested:
            self.first_tested = now
            lead = self.get_lead()
            return True

        if self.first_tested + datetime.timedelta(hours=self.first_tested_hours_ttl) > now:
            return False

        if self.online_since_date is None:
            self.online_since_date = now
            RaspberryPiSession.start(self)

        lead = self.get_lead()
        if lead:
            if lead.status == lead.STATUS_QUALIFIED:
                lead.set_status(lead.STATUS_IN_PROGRESS, edited_by=None)
            for lead_account in lead.lead_accounts.all():
                if lead_account.status == lead_account.STATUS_QUALIFIED:
                    lead_account.set_status(lead_account.STATUS_IN_PROGRESS, edited_by=None)
                    if not lead_account.in_progress_date:
                        lead_account.in_progress_date = now
                        lead_account.save()
                        if lead_account.account_type == lead_account.ACCOUNT_TYPE_GOOGLE:
                            try:
                                lead_account.sync_to_adsdb()
                            except: # pylint: disable=bare-except
                                pass
                if lead_account.status == lead_account.STATUS_SCREENSHOT_QUALIFIED:
                    lead_account.set_status(lead_account.STATUS_SCREENSHOT_NEEDS_APPROVAL, edited_by=None)
                    lead_account.save()

        if not self.first_seen:
            self.first_seen = now
            self.last_seen = now
            return True

        self.last_seen = now
        return True

    def online(self):
        last_seen = self.get_last_seen()
        if last_seen is None:
            return False

        return (timezone.now() - last_seen).total_seconds() < self.online_minutes_ttl * 60

    @classmethod
    def get_objects_online(cls):
        now = timezone.localtime(timezone.now())
        return cls.objects.filter(last_seen__gte=now - datetime.timedelta(minutes=cls.online_minutes_ttl))

    @classmethod
    def get_objects_offline(cls):
        now = timezone.localtime(timezone.now())
        return cls.objects.all().exclude(last_seen__gte=now - datetime.timedelta(minutes=cls.online_minutes_ttl))

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
        if self.last_seen is None or self.first_seen is None:
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

    def reset_cache(self):
        ping_cache_helper = PingCacheHelper()
        ping_data = ping_cache_helper.get(self.rpid)

        if ping_data:
            self.process_ping_data(ping_data)
            ping_cache_helper.delete(self.rpid)

    def get_cache(self):
        ping_cache_helper = PingCacheHelper()
        ping_data = ping_cache_helper.get(self.rpid)
        return ping_data

    def process_ping_data(self, ping_data):
        ip_address = ping_data['ip_address']
        version = ping_data['raspberry_pi_version']
        last_ping = ping_data.get('last_ping')

        lead = self.get_lead()
        if lead and lead.is_active():
            self.update_ping(last_ping)

        if self.ip_address != ip_address:
            self.ip_address = ip_address
        if version and self.version != version:
            self.version = version

        self.restart_required = False
        self.new_config_required = False
        self.version = version

    class Meta:
        db_table = 'raspberry_pi'
