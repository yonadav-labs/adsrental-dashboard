'LeadAccount model'
import requests
from django.utils import timezone
from django.db import models
from django.conf import settings
from django.utils import dateformat
from django_bulk_update.manager import BulkUpdateManager

from adsrental.models.mixins import FulltextSearchMixin
from adsrental.models.lead import Lead
from adsrental.models.lead_change import LeadChange
from adsrental.utils import CustomerIOClient


class LeadAccount(models.Model, FulltextSearchMixin):
    LAST_SECURITY_CHECKPOINT_REPORTED_HOURS_TTL = 48

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

    STATUSES_ACTIVE = [STATUS_AVAILABLE, STATUS_QUALIFIED, STATUS_IN_PROGRESS]

    ACCOUNT_TYPE_FACEBOOK = 'Facebook'
    ACCOUNT_TYPE_GOOGLE = 'Google'
    ACCOUNT_TYPE_CHOICES = [
        (ACCOUNT_TYPE_FACEBOOK, 'Facebook', ),
        (ACCOUNT_TYPE_GOOGLE, 'Google', ),
    ]

    BAN_REASON_AUTO_OFFLINE = 'auto_offline'
    BAN_REASON_AUTO_WRONG_PASSWORD = 'auto_wrong_password'
    BAN_REASON_AUTO_CHECKPOINT = 'auto_checkpoint'

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
        (BAN_REASON_AUTO_OFFLINE, 'Auto: offline for 2 weeks', ),
        (BAN_REASON_AUTO_WRONG_PASSWORD, 'Auto: wrong password for 2 weeks', ),
        (BAN_REASON_AUTO_CHECKPOINT, 'Auto: reported security checkpoint for 2 weeks', ),
        ('Other', 'Other', ),
    )

    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    note = models.TextField(blank=True, null=True, help_text='Not shown when you hover user name in admin interface.')
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='lead_accounts', related_query_name='lead_account')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    old_status = models.CharField(max_length=50, choices=STATUS_CHOICES, null=True, blank=True, default=None, help_text='Used to restore previous status on Unban action')
    ban_reason = models.CharField(max_length=50, choices=BAN_REASON_CHOICES, null=True, blank=True, help_text='Populated from ban form')
    account_type = models.CharField(max_length=50, choices=ACCOUNT_TYPE_CHOICES)
    friends = models.BigIntegerField(default=0)
    url = models.CharField(max_length=255, blank=True, null=True)
    wrong_password_date = models.DateTimeField(blank=True, null=True, help_text='Date when password was reported as wrong.')
    qualified_date = models.DateTimeField(blank=True, null=True, help_text='Date when lead was marked as qualified for the last time.')
    bundler_paid_date = models.DateTimeField(blank=True, null=True, help_text='Date when bundler got his payment for this lead for the last time.')
    bundler_paid = models.BooleanField(default=False, help_text='Is revenue paid to bundler.')
    adsdb_account_id = models.CharField(max_length=255, blank=True, null=True, help_text='Corresponding Account ID in Adsdb database. used for syncing between databases.')
    active = models.BooleanField(default=True, help_text='If false, entry considered as deleted')
    billed = models.BooleanField(default=False, help_text='Did lead receive his payment.')
    last_touch_date = models.DateTimeField(blank=True, null=True, help_text='Date when lead account was touched for the last time.')
    security_checkpoint_date = models.DateTimeField(blank=True, null=True, help_text='Date when security checkpoint has been reported.')
    last_security_checkpoint_reported = models.DateTimeField(blank=True, null=True, help_text='Date when security checkpoint notification was sent.')
    touch_count = models.IntegerField(default=0, help_text='Increased every time you do Touch action for this lead account.')
    auto_ban_enabled = models.BooleanField(default=True, help_text='If true, lead account is banned after two weeks of offline or wrong password.')
    charge_back = models.BooleanField(default=False, help_text='Set to true on auto-ban. True if charge back should be billed to lead.')
    charge_back_billed = models.BooleanField(default=False, help_text='If change back on auto ban billed.')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = BulkUpdateManager()

    class Meta:
        permissions = (
            ("view", "Can access lead account info"),
        )

    def __str__(self):
        if self.account_type == self.ACCOUNT_TYPE_FACEBOOK:
            return 'Facebook lead {}'.format(self.username)
        if self.account_type == self.ACCOUNT_TYPE_GOOGLE:
            return 'Google lead {}'.format(self.username)

        return 'Unknown lead {}'.format(self.username)

    def is_security_checkpoint_reported(self):
        return self.security_checkpoint_date is not None

    def is_wrong_password(self):
        'Is password reported as wrong now'
        return self.wrong_password_date is not None

    def _get_adsdb_api_id(self):
        if self.account_type == self.ACCOUNT_TYPE_FACEBOOK:
            return 146

        if self.account_type == self.ACCOUNT_TYPE_GOOGLE:
            return 147

        raise ValueError()

    def sync_to_adsdb(self):
        'Send lead account info to ADSDB'
        if not settings.ADSDB_SYNC_ENABLED:
            return False

        lead = self.lead
        if lead.company != lead.COMPANY_FBM:
            return False
        if lead.status != lead.STATUS_IN_PROGRESS:
            return False
        if self.account_type == self.ACCOUNT_TYPE_FACEBOOK and self.touch_count < 5:
            return False
        bundler_adsdb_id = lead.bundler and lead.bundler.adsdb_id
        ec2_instance = lead.get_ec2_instance()
        data = dict(
            first_name=lead.first_name,
            last_name=lead.last_name,
            email=self.username,
            last_seen=dateformat.format(lead.raspberry_pi.last_seen, 'j E Y H:i') if lead.raspberry_pi and lead.raspberry_pi.last_seen else None,
            phone=lead.phone,
            ec2_hostname=ec2_instance.hostname if ec2_instance else None,
            utm_source_id=bundler_adsdb_id or settings.DEFAULT_ADSDB_BUNDLER_ID,
            rp_id=lead.raspberry_pi.rpid if lead.raspberry_pi else None,
            api_id=self._get_adsdb_api_id(),
            username=self.username,
        )

        if self.account_type == self.ACCOUNT_TYPE_FACEBOOK:
            data['fb_username'] = self.username
            data['fb_password'] = self.password
        if self.account_type == self.ACCOUNT_TYPE_GOOGLE:
            data['google_username'] = self.username
            data['google_password'] = self.password

        auth = requests.auth.HTTPBasicAuth(settings.ADSDB_USERNAME, settings.ADSDB_PASSWORD)

        if not self.adsdb_account_id:
            url = 'https://www.adsdb.io/api/v1/accounts/create-s'
            response = requests.post(
                url,
                json=[data],
                auth=auth,
            )
            response_json = response.json()
            if response.status_code == 200:
                self.adsdb_account_id = response_json.get('account_data')[0]['id']
                self.save()
                return response_json
            if response.status_code == 409:
                self.adsdb_account_id = response_json.get('account_data')[0]['conflict_id']
                self.save()

        url = 'https://www.adsdb.io/api/v1/accounts/update-s'
        response = requests.post(
            url,
            json={
                'account_id': int(self.adsdb_account_id),
                'data': data,
            },
            auth=auth,
        )

        response_json = response.json()
        return response_json

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
        LeadChange(lead=self.lead, field='status', value=value, old_value=old_value, edited_by=edited_by).save()
        return True

    def ban(self, edited_by, reason=None):
        'Mark lead account as banned, send cutomer.io event.'
        self.ban_reason = reason
        self.save()
        if self.status == LeadAccount.STATUS_AVAILABLE:
            CustomerIOClient().send_lead_event(self.lead, CustomerIOClient.EVENT_AVAILABLE_BANNED)
        else:
            CustomerIOClient().send_lead_event(self.lead, CustomerIOClient.EVENT_BANNED)
        result = self.set_status(LeadAccount.STATUS_BANNED, edited_by)
        if result:
            if not LeadAccount.get_active_lead_accounts(self.lead):
                self.lead.ban(edited_by, reason)
        return result

    def unban(self, edited_by):
        'Restores lead account previous status before banned.'
        self.ban_reason = None
        self.save()
        result = self.set_status(self.old_status or LeadAccount.STATUS_QUALIFIED, edited_by)
        if result:
            self.lead.unban(edited_by)
        return result

    def disqualify(self, edited_by):
        'Set lead account status as disqualified.'
        result = self.set_status(LeadAccount.STATUS_DISQUALIFIED, edited_by)
        if result:
            if not LeadAccount.get_active_lead_accounts(self.lead):
                self.lead.disqualify(edited_by)
        return result

    def qualify(self, edited_by):
        'Set lead account status as qualified.'
        result = self.set_status(LeadAccount.STATUS_QUALIFIED, edited_by)
        if result:
            self.lead.qualify(edited_by)
            self.qualified_date = timezone.now()
            self.save()

        return result

    def is_active(self):
        'Check if RaspberryPi is assigned and lead account is not banned.'
        return self.status in LeadAccount.STATUSES_ACTIVE and self.lead.raspberry_pi is not None

    def is_banned(self):
        'Check if lead account is banned.'
        return self.status == LeadAccount.STATUS_BANNED

    @classmethod
    def get_lead_accounts(cls, lead):
        return cls.objects.filter(lead=lead, active=True)

    @classmethod
    def get_active_lead_accounts(cls, lead):
        return cls.objects.filter(lead=lead, active=True, status__in=cls.STATUSES_ACTIVE)

    def touch(self):
        'Update touch count and last touch date. Tries to sync to adsdb if conditions are met.'
        if self.account_type != self.ACCOUNT_TYPE_FACEBOOK:
            return

        self.last_touch_date = timezone.now()
        self.touch_count += 1
        self.sync_to_adsdb()
        self.save()


class ReadOnlyLeadAccount(LeadAccount):
    'Read only LeadAccount model'
    class Meta:
        proxy = True
        verbose_name = 'Read-only Lead Account'
        verbose_name_plural = 'Read-only Lead Accounts'
