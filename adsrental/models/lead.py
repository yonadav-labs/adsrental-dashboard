from __future__ import unicode_literals

import base64
import datetime

import requests
from xml.etree import ElementTree
from django.utils import timezone
from django.db import models
from django.conf import settings
from django.apps import apps
from django.utils import dateformat

from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.models.lead_change import LeadChange
from adsrental.models.mixins import FulltextSearchMixin
from adsrental.utils import CustomerIOClient, ShipStationClient


class Lead(models.Model, FulltextSearchMixin):
    """
    Stores a single lead entry, related to :model:`adsrental.RaspberryPi` and
    :model:`adsrental.EC2Instance`.

    It is created with status *Available*.

    **How to make lead qualified**

    To change status to qualified, use *Mark as Qualified, Assign RPi, create Shipstation order* admin action.
    This sets status to Qualified, assigns :model:`adsrental.EC2Instance` and :model:`adsrental.EC2Instance` if they are not assigned yet.
    Action does nothing to banned leads.

    **How to ban lead**

    Banned lead does not get payments for beign online and logs from his device are no longer processed.

    To ban lead use *Ban* admin action.
    This action also stops corresponding :model:`adsrental.EC2Instance`.

    **How to unban lead**

    If you unban a lead, it will receive payments fo being online, get RPi firmware updates and process pings for his :model:`adsrental.EC2Instance`.

    To unban lead use *Unban* admin action.
    This action also starts corresponding :model:`adsrental.EC2Instance`.

    **How to check lead status changes**

    Click on lead status. You can see all changes done by backend and admin users for this lead.

    **How to prepare lead for testing**

    Preparation unbans lead if it was banned and resets *first_seen*, *first_tested* and *last_seen* fields, so `Tested` check becomes
    red until backend gets first ping for lead's device.

    To prepare lead for testing use *Prepare for testing* admin action.

    **How to use EC2 RDP for this lead**

    You can connect to corresponding :model:`adsrental.EC2Instance` using RDP. EC2 has Antidetect browser, that you can launch from desktop *Browser.exe*

    To connect to RDP:

    1. click on *RDP* link in *Raspberry Pi* column. In downloads you see file *RP<numbers>.rdp*.
    2. Open this file by double-click with your favorite RDP manager.

    **How to test RaspberryPi device for lead**

    It does not matter if it is inital testing or reshipment, actions are the same:

    1. Use *Prepare for testing* action for this lead. On this form you can specify extra RPIDs to prepare for testing. Paste any data to textarea
       and values like *RP<numbers>* will be prepared for testing as well. Make sure lead status is Qualified.
    2. Download latest firmware if you do not have it: `https://s3-us-west-2.amazonaws.com/mvp-store/pi_1.0.26.zip`
    3. Flash Firmware to SD card using Etcher `https://etcher.io/`
    4. Download `pi.conf` file for this device by clicking *pi.conf* link in admin for this lead
    5. Copy `pi.conf` to SD card root folder.If you are using MacOS/Linux you will see two partitions, use *boot* one.
    6. Safe eject SD card to prevent dataloss.
    7. Insert SD card to RaspberryPi device. If everything is okay, in 10 seconds RaspbeerPi green LED on device should start blinking.
    8. Device can reboot up to 2 times (partition table fix and update to latest patch), so give it at least 3 minutes.
    9. Check `Tested` mark in admin.
    10. Device is ready to be shipped to the end user

    If anything goes wrong, report to @Vlad in Slack.
    """

    STATUS_QUALIFIED = 'Qualified'
    STATUS_DISQUALIFIED = 'Disqualified'
    STATUS_AVAILABLE = 'Available'
    STATUS_IN_PROGRESS = 'In-Progress'
    STATUS_BANNED = 'Banned'
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Available'),
        (STATUS_BANNED, 'Banned'),
        (STATUS_QUALIFIED, 'Qualified'),
        (STATUS_IN_PROGRESS, 'In-Progress'),
        (STATUS_DISQUALIFIED, 'Disqualified'),
    ]

    BAN_REASON_CHOICES = (
        ('Google - Policy', 'Google - Policy', ),
        ('Google - Billing', 'Google - Billing', ),
        ('Google - Unresponsive User', 'Google - Unresponsive User', ),
        ('Facebook - Policy', 'Facebook - Policy', ),
        ('Facebook - Suspicious', 'Facebook - Suspicious', ),
        ('Facebook - Lockout', 'Facebook - Lockout', ),
        ('Facebook - Unresponsive User', 'Facebook - Unresponsive User', ),
        ('Duplicate', 'Duplicate', ),
        ('Bad ad account', 'Bad ad account', ),
        ('Other', 'Other', ),
    )

    DISQUALIFY_REASON_CHOICES = (
        ('Doesn\'t meet friend requirements', 'Doesn\'t meet friend requirements', ),
        ('Doesn\'t meet age requirements', 'Doesn\'t meet age requirements', ),
        ('Fake FB', 'Fake FB', ),
        ('Fake Google', 'Fake Google', ),
        ('Non US account', 'Non US account', ),
        ('Other', 'Other', ),
    )

    COMPANY_EMPTY = '[Empty]'
    COMPANY_ACM = 'ACM'
    COMPANY_FBM = 'FBM'
    COMPANY_ADB = 'ADB'
    COMPANY_CHOICES = (
        (COMPANY_ACM, COMPANY_ACM),
        (COMPANY_FBM, COMPANY_FBM),
        (COMPANY_ADB, COMPANY_ADB),
        (COMPANY_EMPTY, COMPANY_EMPTY),
    )

    STATUSES_ACTIVE = [STATUS_AVAILABLE, STATUS_QUALIFIED, STATUS_IN_PROGRESS]

    leadid = models.CharField(primary_key=True, max_length=255, db_index=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='Available')
    ban_reason = models.CharField(max_length=40, choices=BAN_REASON_CHOICES, null=True, blank=True)
    disqualify_reason = models.CharField(max_length=40, choices=DISQUALIFY_REASON_CHOICES, null=True, blank=True)
    old_status = models.CharField(max_length=40, choices=STATUS_CHOICES, null=True, blank=True, default=None)
    email = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    account_name = models.CharField(max_length=255, blank=True, null=True, unique=True)
    usps_tracking_code = models.CharField(max_length=255, blank=True, null=True)
    utm_source = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    google_account = models.BooleanField(default=False)
    facebook_account = models.BooleanField(default=False)
    shipstation_order_number = models.CharField(max_length=100, null=True, blank=True)
    raspberry_pi = models.OneToOneField('adsrental.RaspberryPi', null=True, blank=True, default=None)
    bundler = models.ForeignKey('adsrental.Bundler', null=True, blank=True, default=None)
    wrong_password = models.BooleanField(default=False)
    wrong_password_date = models.DateTimeField(blank=True, null=True)
    bundler_paid = models.BooleanField(default=False)
    pi_delivered = models.BooleanField(default=False)
    billed = models.BooleanField(default=False)
    tested = models.BooleanField(default=False)
    last_touch_date = models.DateTimeField(blank=True, null=True)
    ship_date = models.DateField(blank=True, null=True)
    qualified_date = models.DateTimeField(blank=True, null=True)
    touch_count = models.IntegerField(default=0)
    facebook_account_status = models.CharField(max_length=255, choices=[(STATUS_AVAILABLE, 'Available'), (STATUS_BANNED, 'Banned')], blank=True, null=True)
    google_account_status = models.CharField(max_length=255, choices=[(STATUS_AVAILABLE, 'Available'), (STATUS_BANNED, 'Banned')], blank=True, null=True)
    fb_email = models.CharField(max_length=255, blank=True, null=True)
    fb_secret = models.CharField(max_length=255, blank=True, null=True)
    google_email = models.CharField(max_length=255, blank=True, null=True)
    google_password = models.CharField(max_length=255, blank=True, null=True)
    fb_friends = models.BigIntegerField(default=0)
    fb_profile_url = models.CharField(max_length=255, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True, default='United States')
    state = models.CharField(max_length=50, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=20, default=COMPANY_EMPTY, choices=COMPANY_CHOICES)
    is_sync_adsdb = models.BooleanField(default=False)
    customerio_enabled = models.BooleanField(default=True)
    photo_id = models.FileField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    splashtop_id = models.CharField(max_length=255, blank=True, null=True)
    adsdb_account_id = models.CharField(max_length=255, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    pi_sent = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.leadid

    class Meta:
        db_table = 'lead'

    def sync_to_adsdb(self):
        if self.company != self.COMPANY_FBM:
            return False
        if self.status != Lead.STATUS_IN_PROGRESS:
            return False
        if self.facebook_account and self.touch_count < 10:
            return False
        bundler_adsdb_id = self.bundler and self.bundler.adsdb_id
        ec2_instance = self.get_ec2_instance()
        data = dict(
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            fb_username=self.fb_email,
            fb_password=self.fb_secret,
            last_seen=dateformat.format(self.raspberry_pi.last_seen, 'j E Y H:i') if self.raspberry_pi and self.raspberry_pi.last_seen else None,
            phone=self.phone,
            ec2_hostname=ec2_instance.hostname if ec2_instance else None,
            utm_source_id=bundler_adsdb_id or settings.DEFAULT_ADSDB_BUNDLER_ID,
            rp_id=self.raspberry_pi.rpid if self.raspberry_pi else None,
        )

        if self.facebook_account:
            data['api_id'] = 146
            data['username'] = self.fb_email
            data['fb_username'] = self.fb_email
            data['fb_password'] = self.fb_secret
        if self.google_account:
            data['api_id'] = 147
            data['username'] = self.google_email
            data['google_username'] = self.google_email
            data['google_password'] = self.google_password

        # import json
        # raise ValueError(json.dumps({
        #             'account_id': int(self.adsdb_account_id),
        #             'data': data,
        #         }))

        if self.adsdb_account_id:
            url = 'https://www.adsdb.io/api/v1/accounts/update-s'
            response = requests.post(
                url,
                json={
                    'account_id': int(self.adsdb_account_id),
                    'data': data,
                },
                auth=requests.auth.HTTPBasicAuth('timothy@adsinc.io', 'timgoat900'),
            )
        else:
            url = 'https://www.adsdb.io/api/v1/accounts/create-s'
            response = requests.post(
                url,
                json=[data],
                auth=requests.auth.HTTPBasicAuth('timothy@adsinc.io', 'timgoat900'),
            )

        result = response.content
        data = response.json()
        if 'id' in data:
            self.adsdb_account_id = data['id']
        self.is_sync_adsdb = True
        self.save()
        return result

    def touch(self):
        self.last_touch_date = timezone.now()
        self.touch_count += 1
        self.sync_to_adsdb()
        self.save()

    def get_address(self):
        return ', '.join([
            self.street or '',
            self.city or '',
            self.state or '',
            self.postal_code or '',
            self.country or '',
        ])

    @classmethod
    def get_online_filter(cls):
        return cls.get_timedelta_filter('raspberry_pi__last_seen__gt', minutes=-RaspberryPi.online_minutes_ttl)

    def get_pi_sent_this_month(self):
        if not self.pi_sent:
            return False
        now = timezone.now()
        if now.year == self.pi_sent.year and now.month == self.pi_sent.month:
            return True

        return False

    def set_status(self, value, edited_by):
        if value not in dict(self.STATUS_CHOICES).keys():
            raise ValueError('Unknown status: {}'.format(value))
        if value == self.status:
            return False

        old_value = self.status

        if value == self.STATUS_BANNED:
            if self.facebook_account:
                self.facebook_account_status = Lead.STATUS_BANNED
            if self.google_account:
                self.google_account_status = Lead.STATUS_BANNED
        else:
            if self.facebook_account:
                self.facebook_account_status = Lead.STATUS_AVAILABLE
            if self.google_account:
                self.google_account_status = Lead.STATUS_AVAILABLE

        if self.status != Lead.STATUS_BANNED:
            self.old_status = self.status

        self.status = value
        self.save()
        LeadChange(lead=self, field='status', value=value, old_value=old_value, edited_by=edited_by).save()
        return True

    def is_ready_for_testing(self):
        if self.raspberry_pi.first_tested:
            return False
        if self.raspberry_pi.first_seen:
            return False

        return True

    def prepare_for_reshipment(self, edited_by):
        old_value = self.pi_delivered
        self.shipstation_order_number = None
        self.pi_delivered = False
        extra_note = 'Prepared for reshipment by {} on {}'.format(
            edited_by,
            timezone.now().strftime('%Y-%m-%d'),
        )
        self.note = '{}\n{}'.format(self.note or '', extra_note)
        self.save()
        raspberry_pi = self.raspberry_pi
        if raspberry_pi:
            raspberry_pi.first_tested = None
            raspberry_pi.last_seen = None
            raspberry_pi.first_seen = None
            raspberry_pi.save()
        LeadChange(lead=self, field='pi_delivered', value=False, old_value=old_value, edited_by=edited_by).save()
        return True

    def ban(self, edited_by, reason=None):
        self.ban_reason = reason
        self.save()
        return self.set_status(Lead.STATUS_BANNED, edited_by)

    def unban(self, edited_by):
        self.ban_reason = None
        self.save()
        return self.set_status(self.old_status or Lead.STATUS_QUALIFIED, edited_by)

    def disqualify(self, edited_by):
        self.set_status(Lead.STATUS_DISQUALIFIED, edited_by)

    def qualify(self, edited_by):
        result = self.set_status(Lead.STATUS_QUALIFIED, edited_by)
        if result:
            self.qualified_date = timezone.now()
            self.save()

    def assign_raspberry_pi(self):
        if not self.raspberry_pi:
            self.raspberry_pi = RaspberryPi.get_free_or_create()
            self.save()
            self.raspberry_pi.leadid = self.leadid
            self.raspberry_pi.first_seen = None
            self.raspberry_pi.last_seen = None
            self.raspberry_pi.first_tested = None
            self.raspberry_pi.save()
            return True

        return False

    def add_shipstation_order(self):
        if not settings.MANAGE_EC2:
            return False

        shipstation_client = ShipStationClient()
        if shipstation_client.get_lead_order_data(self):
            return False
        shipstation_client.add_lead_order(self)
        return True

    def name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def safe_name(self):
        return self.name().encode('ascii', errors='replace')

    def str(self):
        return 'Lead {} ({})'.format(self.name(), self.email)

    def send_web_to_lead(self, request=None):
        response = requests.post(
            'https://webto.salesforce.com/servlet/servlet.WebToLead?encoding=UTF-8',
            data={
                'oid': '00D460000015t1L',
                'first_name': self.first_name,
                'last_name': self.last_name,
                'company': self.company,
                'city': self.city,
                'state': self.status,
                'phone': self.phone,
                'street': self.street,
                'country': self.country,
                'zip': self.postal_code,
                '00N4600000AuUxk': self.leadid,
                'debug': 1,
                'debugEmail': 'volshebnyi@gmail.com',
                '00N46000009vg39': request and request.META.get('REMOTE_ADDR'),
                '00N46000009vg3J': 'ISP',
                '00N46000009wgvp': self.fb_profile_url,
                '00N46000009whHW': self.utm_source,
                '00N46000009whHb': request and request.META.get('HTTP_USER_AGENT'),
                '00N4600000B0zip': 1,
                '00N4600000B1Sup': 'Available',
                'Facebook_Email__c': base64.b64encode(self.fb_email),
                'Facebook_Password__c': base64.b64encode(self.fb_secret),
                'Facebook_Friends__c': self.fb_friends,
                'Account_Name__c': self.account_name,
                'email': self.email,
                'Photo_Id_Url__c': 'https://adsrental.com/app/photo/{}/'.format(base64.b64encode(self.email)),
            }
        )
        return response

    def update_from_shipstation(self, data=None):
        if data is None:
            data = requests.get(
                'https://ssapi.shipstation.com/shipments',
                # params={'shipDateStart': '2017-12-30'},
                params={'orderNumber': self.shipstation_order_number},
                auth=requests.auth.HTTPBasicAuth(settings.SHIPSTATION_API_KEY, settings.SHIPSTATION_API_SECRET),
            ).json().get('shipments')
            data = data[0] if data else {}

        if data and data.get('shipDate'):
            self.ship_date = datetime.datetime.strptime(data.get('shipDate'), '%Y-%m-%d').date()
            self.save()

        if data and data.get('trackingNumber') and self.usps_tracking_code != data.get('trackingNumber'):
            self.usps_tracking_code = data.get('trackingNumber')
            CustomerIOClient().send_lead_event(self, CustomerIOClient.EVENT_SHIPPED, tracking_code=self.usps_tracking_code)
            # self.pi_delivered = True
            self.save()

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
                CustomerIOClient().send_lead_event(self, CustomerIOClient.EVENT_DELIVERED, tracking_code=self.usps_tracking_code)
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

    def is_banned(self):
        return self.status == Lead.STATUS_BANNED


class ReportProxyLead(Lead):
    class Meta:
        proxy = True
        verbose_name = 'Report Lead'
        verbose_name_plural = 'Report Leads'
