from __future__ import unicode_literals

import requests
from xml.etree import ElementTree
from django.utils import timezone
from django.db import models
from django.conf import settings

from adsrental.models.raspberry_pi import RaspberryPi
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

    leadid = models.CharField(primary_key=True, max_length=255, db_index=True)
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
    def upsert_from_sf(sf_lead, lead):
        raspberry_pi = None
        if sf_lead.raspberry_pi:
            old_raspberry_pi = lead.raspberry_pi if lead else None
            if sf_lead.raspberry_pi and not old_raspberry_pi:
                old_raspberry_pi = RaspberryPi.objects.filter(rpid=sf_lead.raspberry_pi.name).first()

            if sf_lead.raspberry_pi and old_raspberry_pi and sf_lead.raspberry_pi.name != old_raspberry_pi.rpid:
                old_raspberry_pi = RaspberryPi.objects.filter(rpid=sf_lead.raspberry_pi.name).first()

            raspberry_pi = RaspberryPi.upsert_from_sf(sf_lead.raspberry_pi, old_raspberry_pi)

        if lead is None:
            lead = Lead(
                leadid=sf_lead.id,
            )

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
            (raspberry_pi.pk if raspberry_pi else None, lead.raspberry_pi.pk if lead.raspberry_pi else None, ),
            (sf_lead.wrong_password, lead.wrong_password, ),
            (sf_lead.bundler_paid, lead.bundler_paid, ),
            (sf_lead.facebook_account_status, lead.facebook_account_status, ),
            (sf_lead.google_account_status, lead.google_account_status, ),
            (sf_lead.raspberry_pi.tested if sf_lead.raspberry_pi else False, lead.tested, ),
            (sf_lead.fb_email, lead.fb_email, ),
            (sf_lead.fb_secret, lead.fb_secret, ),
        ):
            if new_field != old_field:
                break
        else:
            return lead

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
        lead.raspberry_pi = raspberry_pi
        lead.wrong_password = sf_lead.wrong_password
        lead.bundler_paid = sf_lead.bundler_paid
        lead.facebook_account_status = sf_lead.facebook_account_status
        lead.google_account_status = sf_lead.google_account_status
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
        if sf_lead.raspberry_pi:
            old_raspberry_pi = lead.raspberry_pi if lead else None
            if sf_lead.raspberry_pi and not old_raspberry_pi:
                old_raspberry_pi = RaspberryPi.objects.filter(rpid=sf_lead.raspberry_pi.name).first()

            if sf_lead.raspberry_pi and old_raspberry_pi and sf_lead.raspberry_pi.name != old_raspberry_pi.rpid:
                old_raspberry_pi = RaspberryPi.objects.filter(rpid=sf_lead.raspberry_pi.name).first()

            RaspberryPi.upsert_to_sf(sf_lead.raspberry_pi, old_raspberry_pi)

        for new_field, old_field in (
            (sf_lead.raspberry_pi.usps_tracking_code if sf_lead.raspberry_pi else None, lead.usps_tracking_code, ),
            (sf_lead.raspberry_pi.delivered if sf_lead.raspberry_pi else False, lead.pi_delivered, ),
        ):
            if new_field != old_field:
                break
        else:
            return lead

        if sf_lead.raspberry_pi:
            sf_lead.raspberry_pi.usps_tracking_code = lead.usps_tracking_code
            sf_lead.raspberry_pi.delivered = lead.pi_delivered
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
                self.send_customer_io_event('delivered')
            self.save()
