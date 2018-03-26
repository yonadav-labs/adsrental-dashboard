'LeadAccount model'
import requests
from django.db import models
from django.conf import settings
from django.utils import dateformat
from django_bulk_update.manager import BulkUpdateManager

from adsrental.models.mixins import FulltextSearchMixin
from adsrental.models.lead import Lead


class LeadAccount(models.Model, FulltextSearchMixin):
    STATUS_AVAILABLE = 'Available'
    STATUS_BANNED = 'Banned'
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Available'),
        (STATUS_BANNED, 'Banned'),
    ]

    ACCOUNT_TYPE_FACEBOOK = 'Facebook'
    ACCOUNT_TYPE_GOOGLE = 'Google'
    ACCOUNT_TYPE_CHOICES = [
        (ACCOUNT_TYPE_FACEBOOK, 'Facebook', ),
        (ACCOUNT_TYPE_GOOGLE, 'Google', ),
    ]

    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    account_type = models.CharField(max_length=50, choices=ACCOUNT_TYPE_CHOICES)
    friends = models.BigIntegerField(default=0)
    url = models.CharField(max_length=255, blank=True, null=True)
    wrong_password_date = models.DateTimeField(blank=True, null=True, help_text='Date when password was reported as wrong.')
    bundler_paid = models.BooleanField(default=False, help_text='Is revenue paid to bundler.')
    adsdb_account_id = models.CharField(max_length=255, blank=True, null=True, help_text='Corresponding Account ID in Adsdb database. used for syncing between databases.')
    active = models.BooleanField(default=True, help_text='If false, entry considered as deleted')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = BulkUpdateManager()

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
        if lead.company != self.COMPANY_FBM:
            return False
        if lead.status != lead.STATUS_IN_PROGRESS:
            return False
        if self.account_type == self.ACCOUNT_TYPE_FACEBOOK and lead.touch_count < 10:
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
            data['fb_username'] = self.usernamae
            data['fb_password'] = self.password
        if self.account_type == self.ACCOUNT_TYPE_GOOGLE:
            data['google_username'] = self.usernamae
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
