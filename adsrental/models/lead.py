from __future__ import unicode_literals

import requests
from xml.etree import ElementTree
from django.utils import timezone
from django.db import models
from django.conf import settings
from django.apps import apps

from adsrental.models.raspberry_pi import RaspberryPi
from salesforce_handler.models import RaspberryPi as SFRaspberryPi
from adsrental.models.mixins import FulltextSearchMixin
from adsrental.utils import CustomerIOClient


class Lead(models.Model, FulltextSearchMixin):
    STATUS_QUALIFIED = 'Qualified'
    STATUS_AVAILABLE = 'Available'
    STATUS_IN_PROGRESS = 'In-Progress'
    STATUS_BANNED = 'Banned'
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Available'),
        (STATUS_BANNED, 'Banned'),
        (STATUS_QUALIFIED, 'Qualified'),
        (STATUS_IN_PROGRESS, 'In-Progress'),
    ]

    STATUSES_ACTIVE = [STATUS_AVAILABLE, STATUS_QUALIFIED, STATUS_IN_PROGRESS]

    leadid = models.CharField(primary_key=True, max_length=255, db_index=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='Available')
    old_status = models.CharField(max_length=40, choices=STATUS_CHOICES, null=True, blank=True, default=None)
    email = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    account_name = models.CharField(max_length=255, blank=True, null=True)
    usps_tracking_code = models.CharField(max_length=255, blank=True, null=True)
    utm_source = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    google_account = models.BooleanField(default=False)
    facebook_account = models.BooleanField(default=False)
    raspberry_pi = models.OneToOneField('adsrental.RaspberryPi', null=True, blank=True, default=None)
    wrong_password = models.BooleanField(default=False)
    bundler_paid = models.BooleanField(default=False)
    pi_delivered = models.BooleanField(default=False)
    tested = models.BooleanField(default=False)
    facebook_account_status = models.CharField(max_length=255, choices=[(STATUS_AVAILABLE, 'Available'), (STATUS_BANNED, 'Banned')], blank=True, null=True)
    google_account_status = models.CharField(max_length=255, choices=[(STATUS_AVAILABLE, 'Available'), (STATUS_BANNED, 'Banned')], blank=True, null=True)
    fb_email = models.CharField(max_length=255, blank=True, null=True)
    fb_secret = models.CharField(max_length=255, blank=True, null=True)
    is_sync_adsdb = models.BooleanField(default=False)
    photo_id = models.FileField(blank=True, null=True)
    splashtop_id = models.CharField(max_length=255, blank=True, null=True)
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

    def ban(self):
        if self.status == Lead.STATUS_BANNED:
            return False
        self.old_status = self.status
        self.status = Lead.STATUS_BANNED
        if self.facebook_account:
            self.facebook_account_status = Lead.STATUS_BANNED
        if self.google_account:
            self.google_account_status = Lead.STATUS_BANNED
        self.save()
        self.ec2instance.stop()
        self.send_customer_io_event('banned')
        return True

    def unban(self):
        if self.status != self.STATUS_BANNED:
            return False
        self.status = self.old_status or Lead.STATUS_QUALIFIED
        if self.facebook_account:
            self.facebook_account_status = Lead.STATUS_AVAILABLE
        if self.google_account:
            self.google_account_status = Lead.STATUS_AVAILABLE
        self.save()
        return True

    @staticmethod
    def upsert_from_sf(sf_lead, lead):
        if lead is None:
            lead = Lead(
                leadid=sf_lead.id,
            )

        local_raspberry_pi = lead.raspberry_pi if lead else None
        local_raspberry_pi_rpid = local_raspberry_pi.rpid if local_raspberry_pi else None
        remote_raspberry_pi = sf_lead.raspberry_pi if sf_lead else None
        remote_raspberry_pi_rpid = remote_raspberry_pi.name if remote_raspberry_pi else None

        address = ', '.join([
            sf_lead.street or '',
            sf_lead.city or '',
            sf_lead.state or '',
            sf_lead.postal_code or '',
            sf_lead.country or '',
        ])

        for new_field, old_field in (
            (sf_lead.first_name, lead.first_name, ),
            (sf_lead.last_name, lead.last_name, ),
            (sf_lead.email, lead.email, ),
            (sf_lead.phone, lead.phone, ),
            (address, lead.address, ),
            (sf_lead.account_name, lead.account_name, ),
            (sf_lead.status, lead.status, ),
            # (sf_lead.raspberry_pi.usps_tracking_code if sf_lead.raspberry_pi else None, lead.usps_tracking_code, ),
            # (sf_lead.raspberry_pi.delivered if sf_lead.raspberry_pi else False, lead.pi_delivered, ),
            (sf_lead.utm_source, lead.utm_source, ),
            (sf_lead.google_account, lead.google_account, ),
            (remote_raspberry_pi_rpid, local_raspberry_pi_rpid, ),
            (sf_lead.wrong_password, lead.wrong_password, ),
            (sf_lead.bundler_paid, lead.bundler_paid, ),
            (sf_lead.facebook_account_status, lead.facebook_account_status, ),
            (sf_lead.google_account_status, lead.google_account_status, ),
            (sf_lead.raspberry_pi.tested if sf_lead.raspberry_pi else False, lead.tested, ),
            (sf_lead.fb_email, lead.fb_email, ),
            (sf_lead.fb_secret, lead.fb_secret, ),
            (sf_lead.splashtop_id, lead.splashtop_id, ),
        ):
            if new_field != old_field:
                break
        else:
            return lead

        new_raspberry_pi = RaspberryPi.objects.filter(rpid=remote_raspberry_pi_rpid).first()
        try:
            if new_raspberry_pi and new_raspberry_pi.lead and new_raspberry_pi.lead.pk != lead.pk:
                new_raspberry_pi = None
        except Lead.DoesNotExist:
            pass

        lead.first_name = sf_lead.first_name
        lead.last_name = sf_lead.last_name
        lead.email = sf_lead.email
        lead.phone = sf_lead.phone
        lead.address = address
        lead.account_name = sf_lead.account_name
        lead.status = sf_lead.status
        # lead.usps_tracking_code = sf_lead.raspberry_pi.usps_tracking_code if sf_lead.raspberry_pi else None
        # lead.pi_delivered = sf_lead.raspberry_pi.delivered if sf_lead.raspberry_pi else False
        lead.utm_source = sf_lead.utm_source
        lead.google_account = sf_lead.google_account
        lead.facebook_account = sf_lead.facebook_account
        lead.raspberry_pi = new_raspberry_pi
        lead.wrong_password = sf_lead.wrong_password
        lead.bundler_paid = sf_lead.bundler_paid
        lead.splashtop_id = sf_lead.splashtop_id
        lead.facebook_account_status = sf_lead.facebook_account_status
        lead.google_account_status = sf_lead.google_account_status
        if not lead.tested:
            lead.tested = sf_lead.raspberry_pi.tested if sf_lead.raspberry_pi else False
        lead.fb_email = sf_lead.fb_email
        lead.fb_secret = sf_lead.fb_secret
        lead.save()
        return lead

    def name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def str(self):
        return 'Lead {} ({})'.format(self.name(), self.email)

    @staticmethod
    def upsert_to_sf_thread(params):
        try:
            Lead.upsert_to_sf(*params)
        except Exception as e:
            return {'email': params[1].email, 'error': str(e), 'result': False}

        return {'email': params[1].email, 'result': True}

    @staticmethod
    def upsert_to_sf(sf_lead, lead):
        local_raspberry_pi = lead.raspberry_pi if lead else None
        local_raspberry_pi_rpid = local_raspberry_pi.rpid if local_raspberry_pi else None
        remote_raspberry_pi = sf_lead.raspberry_pi if sf_lead else None
        remote_raspberry_pi_rpid = remote_raspberry_pi.name if remote_raspberry_pi else None

        if sf_lead.raspberry_pi and lead.raspberry_pi:
            lead.raspberry_pi.upsert_to_sf(sf_lead.raspberry_pi, lead.raspberry_pi)

        for new_field, old_field in (
            (sf_lead.raspberry_pi.usps_tracking_code if sf_lead.raspberry_pi else None, lead.usps_tracking_code, ),
            (sf_lead.raspberry_pi.delivered if sf_lead.raspberry_pi else False, lead.pi_delivered, ),
            (sf_lead.raspberry_pi.tested if sf_lead.raspberry_pi else False, lead.tested, ),
            (sf_lead.splashtop_id, lead.splashtop_id, ),
            (local_raspberry_pi_rpid, remote_raspberry_pi_rpid, ),
            (sf_lead.status, lead.status, ),
        ):
            if new_field != old_field:
                break
        else:
            return lead

        sf_lead.raspberry_pi = SFRaspberryPi.objects.filter(name=local_raspberry_pi_rpid).first()
        sf_lead.splashtop_id = lead.splashtop_id
        sf_lead.status = lead.status
        sf_lead.last_modified_by_id = settings.SALESFORCE_API_USER_ID
        sf_lead.save()

        if sf_lead.raspberry_pi:
            sf_lead.raspberry_pi.usps_tracking_code = lead.usps_tracking_code
            sf_lead.raspberry_pi.delivered = lead.pi_delivered
            sf_lead.raspberry_pi.tested = lead.tested
            sf_lead.raspberry_pi.save()

        return lead

    def update_from_shipstation(self, data=None):
        if data is None:
            data = requests.get(
                'https://ssapi.shipstation.com/shipments',
                # params={'shipDateStart': '2017-12-30'},
                params={'orderNumber': self.account_name},
                auth=requests.auth.HTTPBasicAuth(settings.SHIPSTATION_API_KEY, settings.SHIPSTATION_API_SECRET),
            ).json().get('shipments')
            data = data[0] if data else {}
        if data and data.get('trackingNumber') and self.usps_tracking_code != data.get('trackingNumber'):
            self.usps_tracking_code = data.get('trackingNumber')
            self.send_customer_io_event('shipped', tracking_code=self.usps_tracking_code)
            # self.pi_delivered = True
            self.save()

    def send_customer_io_event(self, event, **kwargs):
        CustomerIOClient().send_lead_event(self, event, **kwargs)

    def update_pi_delivered(self):
        if not self.usps_tracking_code:
            return

        xml = '<TrackRequest USERID="039ADCRU4974"><TrackID ID="{}"></TrackID></TrackRequest>'.format(self.usps_tracking_code)
        url = 'https://secure.shippingapis.com/ShippingAPI.dll'
        response = requests.get(url, params={
            'API': 'TrackV2',
            'xml': xml,
        })

        tree = ElementTree.fromstring(response.text)
        pi_delivered = False
        try:
            pi_delivered = 'delivered' in tree.find('TrackInfo').getchildren()[0].text
        except:
            pass

        if self.pi_delivered != pi_delivered:
            self.pi_delivered = pi_delivered
            if self.pi_delivered:
                self.send_customer_io_event('delivered', tracking_code=self.usps_tracking_code)
            self.save()

    def check_ec2_status(self):
        ec2_instance = self.get_ec2_instance()
        if not ec2_instance:
            return

        ec2_instance.update_from_boto()
        EC2Instance = apps.get_app_config('adsrental').get_model('EC2Instance')
        if self.status in self.STATUSES_ACTIVE and self.raspberry_pi and not ec2_instance:
            EC2Instance.launch_for_lead(self)
        if self.status in self.STATUSES_ACTIVE and self.raspberry_pi and not ec2_instance.is_running():
            EC2Instance.launch_for_lead(self)
        if self.status not in self.STATUSES_ACTIVE and ec2_instance and ec2_instance.is_running():
            ec2_instance.stop()

    def get_ec2_instance(self):
        ec2_instance = None
        try:
            ec2_instance = self.ec2instance
        except:
            pass
        return ec2_instance

    def is_active(self):
        return self.status in Lead.STATUSES_ACTIVE and self.raspberry_pi is not None

    def find_ec2_instance_errors(self):
        errors = []
        ec2_instance = self.get_ec2_instance()

        if self.status not in self.STATUSES_ACTIVE and ec2_instance and ec2_instance.is_running():
            errors.append('Lead is not active but instance is running')
        if self.status in self.STATUSES_ACTIVE and self.raspberry_pi and not ec2_instance:
            errors.append('Lead is active and has RPI assigned, but no EC2 instance')
        if self.status in self.STATUSES_ACTIVE and self.raspberry_pi and ec2_instance and not ec2_instance.is_running():
            errors.append('Lead is active and has RPI assigned, but  EC is not running')
        if self.status in self.STATUSES_ACTIVE and self.raspberry_pi and not self.raspberry_pi.online():
            errors.append('Lead is active and has RPI and EC2 assigned, but RPi is not running. RPi should be restarted.')

        if ec2_instance and ec2_instance.is_running():
            if not ec2_instance.ssh_up:
                errors.append('SSH connection to EC2 instance failed. EC2 should be restarted.')
            if not ec2_instance.web_up:
                errors.append('EC2 web interface is not responding. EC2 should be restarted.')
            if not ec2_instance.tunnel_up and self.raspberry_pi.online():
                errors.append('EC2 SSH tunnel to RPi is down, but RPi seems to be online. RPi should be restarted.')
            if not ec2_instance.tunnel_up and not self.raspberry_pi.online():
                errors.append('EC2 SSH tunnel to RPi is down, and RPi seems to be offline. Check RPI internet connection and restart it.')

            if ec2_instance.tunnel_up and self.raspberry_pi and self.raspberry_pi.version == settings.OLD_RASPBERRY_PI_VERSION:
                errors.append('RPi still runs old version {}. Autoupdating it over tunnel.'.format(self.raspberry_pi.version))
            if not ec2_instance.tunnel_up and self.raspberry_pi and self.raspberry_pi.version == settings.OLD_RASPBERRY_PI_VERSION:
                errors.append('RPi still runs old version {}. Tunnel is down, ask {} to reset RPi manually.'.format(self.raspberry_pi.version, self.name()))
            if ec2_instance.tunnel_up and self.raspberry_pi and self.raspberry_pi.online() and self.raspberry_pi.version != settings.RASPBERRY_PI_VERSION:
                errors.append('RPi still runs version {} and is online. RPi updater will update it soon.'.format(self.raspberry_pi.version))
            if ec2_instance.tunnel_up and self.raspberry_pi and not self.raspberry_pi.online() and self.raspberry_pi.version != settings.RASPBERRY_PI_VERSION:
                errors.append('RPi still runs version {} but is offline. RPi updater will update it soon.'.format(self.raspberry_pi.version))

        return errors

    def find_raspberry_pi_errors(self):
        errors = []
        if self.status == Lead.STATUS_QUALIFIED and not self.raspberry_pi:
            errors.append('Lead is qualified but RaspberryPi is not assigned')
        # if self.is_active() and self.raspberry_pi and not self.raspberry_pi.online():
        #     errors.append('Lead is active but RaspberryPi is offline')
        if self.status == Lead.STATUS_QUALIFIED and self.raspberry_pi and not self.raspberry_pi.first_tested:
            errors.append('Lead is qualified but RaspberryPi is not tested')

        return errors

    def find_errors(self):
        return self.find_ec2_instance_errors() + self.find_raspberry_pi_errors()
