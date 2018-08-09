'Lead model'
import datetime
import re

from xml.etree import ElementTree
import requests
from django.utils import timezone
from django.db import models
from django.conf import settings
from django_bulk_update.manager import BulkUpdateManager

from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.models.lead_change import LeadChange
from adsrental.models.mixins import FulltextSearchMixin
from adsrental.utils import CustomerIOClient, ShipStationClient, PingCacheHelper


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
    class Meta:
        db_table = 'lead'
        permissions = (
            ("view", "Can access lead info"),
        )

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

    SHIPSTATION_ORDER_STATUS_SHIPPED = 'shipped'
    SHIPSTATION_ORDER_STATUS_AWAITING_SHIPMENT = 'awaiting_shipment'
    SHIPSTATION_ORDER_STATUS_ON_HOLD = 'on_hold'
    SHIPSTATION_ORDER_STATUS_CANCELLED = 'cancelled'
    SHIPSTATION_ORDER_STATUS_CHOICES = (
        (SHIPSTATION_ORDER_STATUS_SHIPPED, 'Shipped', ),
        (SHIPSTATION_ORDER_STATUS_AWAITING_SHIPMENT, 'Awaiting', ),
        (SHIPSTATION_ORDER_STATUS_ON_HOLD, 'On Hold', ),
        (SHIPSTATION_ORDER_STATUS_CANCELLED, 'Cancelled', ),
    )

    leadid = models.CharField(primary_key=True, max_length=255, db_index=True, help_text='UUID is now used as a primary key for lead')
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='Available', help_text='All statuses except for Banned are considered as Active')
    email = models.CharField(max_length=255, blank=True, null=True, unique=True, help_text='Should be unique')
    note = models.TextField(blank=True, null=True, help_text='Not shown when you hover user name in admin interface.')
    old_status = models.CharField(max_length=40, choices=STATUS_CHOICES, null=True, blank=True, default=None, help_text='Used to restore previous status on Unban action')
    phone = models.CharField(max_length=255, blank=True, null=True, help_text='Formatted phone number')
    account_name = models.CharField(max_length=255, blank=True, null=True, help_text='Obsolete, was used in SF, should be removed')
    usps_tracking_code = models.CharField(max_length=255, blank=True, null=True, help_text='Tracking code. Populated by sync_from-shipstation once order is shipped')
    utm_source = models.CharField(max_length=255, blank=True, null=True, db_index=True, help_text='Bundler UTM. Obsolete, use bundler instead')
    shipstation_order_number = models.CharField(max_length=100, null=True, blank=True, help_text='Populated on mark as qualified, when SS ordeer is created.')
    shipstation_order_status = models.CharField(choices=SHIPSTATION_ORDER_STATUS_CHOICES, max_length=100, null=True, blank=True, help_text='Populated by cron script.')
    raspberry_pi = models.OneToOneField(RaspberryPi, null=True, blank=True, default=None, db_index=True, help_text='Linked RaspberryPi device', on_delete=models.SET_NULL)
    bundler = models.ForeignKey('adsrental.Bundler', null=True, blank=True, default=None, help_text='New UTM source representation', on_delete=models.SET_DEFAULT)
    pi_delivered = models.BooleanField(default=False, help_text='Is RaspberryPi delivered to end user.')
    delivery_date = models.DateField(default=None, null=True, blank=True, help_text='When RaspberryPi delivered to end user.')
    billed = models.BooleanField(default=False, help_text='Account billed to Ads Inc.')
    tested = models.BooleanField(default=False, help_text='Obsolete field. Use first_tested instead.')
    last_touch_date = models.DateTimeField(blank=True, null=True, help_text='Date when lead was touched for the last time.')
    ship_date = models.DateField(blank=True, null=True, help_text='Date when order was shipped. Populated from shipstation sync.')
    touch_count = models.IntegerField(default=0, help_text='Increased every time you do Touch action for this lead.')
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True, default='United States')
    state = models.CharField(max_length=50, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=20, default=COMPANY_EMPTY, choices=COMPANY_CHOICES)
    customerio_enabled = models.BooleanField(default=True, help_text='If False, customer.io event will not be sent for this lead. However, they are created.')
    is_reimbursed = models.BooleanField(default=False, help_text='Lead is active for more than 5 months and gets pay checks.')
    photo_id = models.FileField(blank=True, null=True, help_text='Photo uploaded by user on registration.')
    extra_photo_id = models.FileField(blank=True, null=True, help_text='Extra photo uploaded by user on registration.')
    splashtop_id = models.CharField(max_length=255, blank=True, null=True, help_text='Splashtop ID reported by user.')
    tracking_info = models.TextField(blank=True, null=True, help_text='Raw response from secure.shippingapis.com')
    pi_sent = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = BulkUpdateManager()

    def __str__(self):
        return self.leadid

    def is_wrong_password(self):
        'Is password reported as wrong now'
        for lead_account in self.lead_accounts.all():
            if lead_account.active and lead_account.wrong_password_date:
                return True

        return False

    def is_wrong_password_google(self):
        'Is password reported as wrong now for google account'
        for lead_account in self.lead_accounts.all():
            if lead_account.active and lead_account.account_type == lead_account.ACCOUNT_TYPE_GOOGLE and lead_account.wrong_password_date:
                return True

        return False

    def is_wrong_password_facebook(self):
        'Is password reported as wrong nowc'
        for lead_account in self.lead_accounts.all():
            if lead_account.active and lead_account.account_type == lead_account.ACCOUNT_TYPE_FACEBOOK and lead_account.wrong_password_date:
                return True

        return False

    def is_security_checkpoint_reported(self):
        'Is password reported as wrong now'
        for lead_account in self.lead_accounts.all():
            if lead_account.active and lead_account.security_checkpoint_date:
                return True

        return False

    def is_bundler_paid(self):
        'Is bundler paid for any account'
        for lead_account in self.lead_accounts.all():
            if lead_account.active and lead_account.bundler_paid:
                return True

        return False

    def touch(self):
        'Update touch count and last touch date. Tries to sync to adsdb if conditions are met.'
        self.last_touch_date = timezone.now()
        self.touch_count += 1
        self.save()
        for lead_account in self.lead_accounts.all():
            lead_account.touch()

    def get_address(self):
        'Get address as a string.'
        return ', '.join([
            self.street or '',
            self.city or '',
            self.state or '',
            self.postal_code or '',
            self.country or '',
        ])

    def get_phone_formatted(self):
        'Get phone to show to end user.'
        if not self.phone:
            return None

        if self.phone.startswith('('):
            return self.phone

        return '({}) {}-{}'.format(self.phone[0:3], self.phone[3:6], self.phone[6:])

    @classmethod
    def get_online_filter(cls):
        '''
        Get online condition ty use as a filter like

        Lead.objects.filter(Lead.get_online_filter())
        '''
        return cls.get_timedelta_filter('raspberry_pi__last_seen__gt', minutes=-RaspberryPi.online_minutes_ttl)

    def get_pi_sent_this_month(self):
        'Obsolete.'
        if not self.pi_sent:
            return False
        now = timezone.localtime(timezone.now())
        if now.year == self.pi_sent.year and now.month == self.pi_sent.month:
            return True

        return False

    def set_status(self, value, edited_by):
        'Change status, create LeadChangeinstance.'
        if value not in dict(self.STATUS_CHOICES).keys():
            raise ValueError('Unknown status: {}'.format(value))
        if value == self.status:
            return False

        old_value = self.status

        if value == self.STATUS_QUALIFIED and old_value == self.STATUS_IN_PROGRESS:
            return False

        if self.status != Lead.STATUS_BANNED:
            self.old_status = self.status

        self.status = value
        self.save()
        LeadChange(lead=self, field='status', value=value, old_value=old_value, edited_by=edited_by).save()
        return True

    def is_ready_for_testing(self):
        'Check if RaspberryPi is ready to be tested.'
        if not self.raspberry_pi:
            return False
        if self.raspberry_pi.first_tested:
            return False
        if self.raspberry_pi.first_seen:
            return False

        return True

    def prepare_for_reshipment(self, edited_by):
        'Clear timestamps, perepare for testing, create LeadChange.'
        old_value = self.pi_delivered
        self.shipstation_order_number = None
        self.shipstation_order_status = None
        self.pi_delivered = False
        now = timezone.localtime(timezone.now())
        extra_note = 'Prepared for reshipment by {} on {}'.format(
            edited_by,
            now.strftime('%Y-%m-%d'),
        )
        self.note = '{}\n{}'.format(self.note or '', extra_note)
        self.save()
        raspberry_pi = self.raspberry_pi
        if raspberry_pi:
            raspberry_pi.first_tested = None
            raspberry_pi.last_seen = None
            raspberry_pi.first_seen = None
            raspberry_pi.save()
        LeadChange(lead=self, field='prepare_for_reshipment', value=False, old_value=old_value, edited_by=edited_by).save()
        return True

    def ban(self, edited_by):
        'Mark lead as banned, send cutomer.io event.'
        result = self.set_status(Lead.STATUS_BANNED, edited_by)
        return result

    def unban(self, edited_by):
        'Restores lead previous status before banned.'
        result = self.set_status(self.old_status or Lead.STATUS_QUALIFIED, edited_by)
        return result

    def disqualify(self, edited_by):
        'Set lead status as disqualified.'
        return self.set_status(Lead.STATUS_DISQUALIFIED, edited_by)

    def qualify(self, edited_by):
        'Set lead status as qualified.'
        result = self.set_status(Lead.STATUS_QUALIFIED, edited_by)
        return result

    def assign_raspberry_pi(self):
        'Assign new or existing RaspberryPi if does not exist, prepare it for testing.'
        if self.raspberry_pi:
            return False

        self.raspberry_pi = RaspberryPi.create()
        self.save()
        self.raspberry_pi.leadid = self.leadid
        self.raspberry_pi.first_seen = None
        self.raspberry_pi.last_seen = None
        self.raspberry_pi.first_tested = None
        self.raspberry_pi.save()
        return True

    def add_shipstation_order(self):
        'Create shipstation order if does not exist.'
        if not settings.MANAGE_SHIPSTATION:
            return False

        shipstation_client = ShipStationClient()
        if shipstation_client.get_lead_order_data(self):
            return False
        shipstation_client.add_lead_order(self)
        return True

    def name(self):
        'get first and last name as a single string.'
        return '{} {}'.format(self.first_name, self.last_name)

    def safe_name(self):
        'Use only ascii characters for name to send to shipstation, for example.'
        return self.name().encode('ascii', errors='replace').decode()

    def str(self):
        'Obsolete.'
        return 'Lead {} ({})'.format(self.name(), self.email)

    def update_from_shipstation(self, data=None):
        'Set tracking number if item was sent, set ship_date if empty.'
        if data is None:
            data = requests.get(
                'https://ssapi.shipstation.com/shipments',
                # params={'shipDateStart': '2017-12-30'},
                params={'orderNumber': self.shipstation_order_number},
                auth=requests.auth.HTTPBasicAuth(settings.SHIPSTATION_API_KEY, settings.SHIPSTATION_API_SECRET),
            ).json().get('shipments')
            data = data[0] if data else {}

        if data and data.get('shipDate') and not self.ship_date:
            self.ship_date = datetime.datetime.strptime(data.get('shipDate'), '%Y-%m-%d').date()
            self.save()

        if data and data.get('trackingNumber') and self.usps_tracking_code != data.get('trackingNumber'):
            self.usps_tracking_code = data.get('trackingNumber')
            CustomerIOClient().send_lead_event(self, CustomerIOClient.EVENT_SHIPPED, tracking_code=self.usps_tracking_code)
            # self.pi_delivered = True
            self.save()

    def update_pi_delivered(self, pi_delivered, tracking_info_xml):
        'Set pi_delivered and tracking_info'
        if pi_delivered is None:
            return

        self.tracking_info = tracking_info_xml
        self.pi_delivered = pi_delivered

        if pi_delivered:
            dates = re.findall(r'\S+ \d{1,2}, \d{4}', tracking_info_xml)
            if dates:
                try:
                    self.delivery_date = datetime.datetime.strptime(dates[0], '%B %d, %Y').date()
                except ValueError:
                    pass
        else:
            self.delivery_date = None

    def get_shippingapis_tracking_info(self):
        'Get tracking info as XML string from secure.shippingapis.com'
        if not self.usps_tracking_code:
            return None

        xml = '<TrackRequest USERID="039ADCRU4974"><TrackID ID="{}"></TrackID></TrackRequest>'.format(self.usps_tracking_code)
        url = 'https://secure.shippingapis.com/ShippingAPI.dll'
        try:
            response = requests.get(url, params={
                'API': 'TrackV2',
                'xml': xml,
            })
        except requests.exceptions.ConnectionError:
            return None

        return response.text

    def get_pi_delivered_from_xml(self, tracking_info_xml):
        'Check XML string secure.shippingapis.com if device had been delivered.'
        if tracking_info_xml is None:
            return None
        try:
            tree = ElementTree.fromstring(tracking_info_xml)
        except ElementTree.ParseError:
            return None

        track_info = tree.find('TrackInfo')
        if track_info is None:
            return None

        track_summary = track_info.find('TrackSummary')
        if track_summary is not None and track_summary.text and 'was delivered' in track_summary.text.lower():
            return True
        # track_details = track_info.findall('TrackDetail')
        # for track_detail in track_details:
        #     if not track_detail.text:
        #         continue
        #     if 'delivered' in track_detail.text.lower():
        #         return True

        return False

    def get_ec2_instance(self):
        'Get corresponding EC2 object.'
        try:
            return self.ec2instance # pylint: disable=E1101
        except Lead.ec2instance.RelatedObjectDoesNotExist: # pylint: disable=E1101
            return None

    def is_active(self):
        'Check if RaspberryPi is assigned and lead is not banned.'
        return self.status in Lead.STATUSES_ACTIVE and self.raspberry_pi is not None

    @classmethod
    def is_status_active(cls, status):
        'Check if status is not banned.'
        return status in cls.STATUSES_ACTIVE

    def is_banned(self):
        'Check if lead is banned.'
        return self.status == Lead.STATUS_BANNED

    def clear_ping_cache(self):
        'Remove ping cache for this lead. Obsolete.'
        if self.raspberry_pi:
            PingCacheHelper().delete(self.raspberry_pi.rpid)

    def sync_to_adsdb(self):
        result = False
        for lead_account in self.lead_accounts.filter(active=True):
            result = lead_account.sync_to_adsdb()

        return result

    def get_qualified_date(self):
        for lead_account in self.lead_accounts.all():
            return lead_account.qualified_date

        return None

    def is_order_on_hold(self):
        return self.shipstation_order_status == Lead.SHIPSTATION_ORDER_STATUS_ON_HOLD


class ReportProxyLead(Lead):
    'A proxy model to register Lead in admin UI twice for Reports'
    class Meta:
        proxy = True
        verbose_name = 'Report Lead'
        verbose_name_plural = 'Report Leads'


class ReadOnlyLead(Lead):
    'Read only Lead model'
    class Meta:
        proxy = True
        verbose_name = 'Read-only Lead'
        verbose_name_plural = 'Read-only Leads'
