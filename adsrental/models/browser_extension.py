import string

from django.db import models


class BrowserExtension(models.Model):
    class Meta:
        verbose_name = 'Browser Extension'
        verbose_name_plural = 'Browser Extensions'

    salesforce_id = models.CharField(max_length=255, db_index=True, null=True)
    name = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    last_modified_date = models.DateTimeField(null=True, blank=True)
    last_modified_by_id = models.CharField(max_length=255, null=True, blank=True)
    connection_sent_id = models.CharField(max_length=255, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    version = models.CharField(max_length=255, null=True, blank=True)
    system_mod_stamp = models.DateTimeField(null=True, blank=True)
    last_referenced_date = models.DateTimeField(null=True, blank=True)
    fb_updated_secret = models.CharField(max_length=255, null=True, blank=True)
    owner_id = models.CharField(max_length=255, null=True, blank=True)
    connection_reveived_id = models.CharField(max_length=255, null=True, blank=True)
    ad_account_status_last_checked = models.CharField(max_length=255, null=True, blank=True)
    fb_friends = models.CharField(max_length=255, null=True, blank=True)
    secret_changed = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)
    log_file_link = models.TextField(max_length=1024, null=True, blank=True)
    created_date = models.DateTimeField(null=True, blank=True)
    fb_secret = models.CharField(max_length=255, null=True, blank=True)
    last_viewed_date = models.DateTimeField(null=True, blank=True)
    ad_account_status = models.CharField(max_length=255, null=True, blank=True)
    ad_account_active = models.BooleanField(default=False)
    status = models.CharField(max_length=255, null=True, blank=True)
    login_notifications_disabled = models.BooleanField(default=False)
    created_by_id = models.CharField(max_length=255, null=True, blank=True)
    fb_email = models.CharField(max_length=255, null=True, blank=True)
    ip_address = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

    @staticmethod
    def str_printable(s):
        printable = set(string.printable)
        return filter(lambda x: x in printable, s)

    @classmethod
    def upsert_from_sf(cls, data):
        item, created = cls.objects.update_or_create(
            salesforce_id=data['ID'],
            defaults=dict(
                last_modified_date=data['LASTMODIFIEDDATE'] or None,
                last_modified_by_id=data['LASTMODIFIEDBYID'],
                connection_sent_id=data['CONNECTIONSENTID'],
                is_deleted=data['ISDELETED'] == 'true',
                version=data['VERSION__C'],
                system_mod_stamp=data['SYSTEMMODSTAMP'] or None,
                last_referenced_date=data['LASTREFERENCEDDATE'] or None,
                fb_updated_secret=data['FB_UPDATED_SECRET__C'],
                owner_id=data['OWNERID'],
                connection_reveived_id=data['CONNECTIONRECEIVEDID'],
                ad_account_status_last_checked=data['AD_ACCOUNT_STATUS_LAST_CHECKED__C'] or None,
                fb_friends=data['FB_FRIENDS__C'],
                secret_changed=data['SECRET_CHANGED__C'] == 'true',
                last_seen=data['LAST_SEEN__C'] or None,
                log_file_link=data['LOG_FILE_LINK__C'],
                created_date=data['CREATEDDATE'] or None,
                fb_secret=data['FB_SECRET__C'],
                last_viewed_date=data['LASTVIEWEDDATE'] or None,
                ad_account_status=cls.str_printable(data['AD_ACCOUNT_STATUS__C']),
                ad_account_active=data['AD_ACCOUNT_ACTIVE__C'] == 'true',
                status=data['STATUS__C'],
                name=data['NAME'],
                login_notifications_disabled=data['LOGIN_NOTIFICATIONS_DISABLED__C'] == 'true',
                created_by_id=data['CREATEDBYID'],
                fb_email=data['FB_EMAIL__C'],
                ip_address=data['IP_ADDRESS__C'],
            ),
        )
        item.save()

# {
#     'LASTMODIFIEDDATE': '2017-08-31T08:53:22.000Z',
#     'LASTMODIFIEDBYID': '00546000000rlLVAAY',
#     'CONNECTIONSENTID': '',
#     'ISDELETED': 'false',
#     'VERSION__C': '0.0.0.4',
#     'ID': 'a0346000002htWUAAY',
#     'SYSTEMMODSTAMP': '2017-08-31T08:53:22.000Z',
#     'LASTREFERENCEDDATE': '',
#     'FB_UPDATED_SECRET__C': '',
#     'OWNERID': '00546000000rlLVAAY',
#     'CONNECTIONRECEIVEDID': '',
#     'AD_ACCOUNT_STATUS_LAST_CHECKED__C': '',
#     'FB_FRIENDS__C': '',
#     'SECRET_CHANGED__C': 'false',
#     'LAST_SEEN__C': '2017-08-31T08:53:22.000Z',
#     'LOG_FILE_LINK__C': '<a href="https://adsrental.com/log/d66098cb5db5937e223e6ffeb855f3f5ade873e18b83d9854978dae869c110" target="_blank">https://adsrental.com/log/d66098cb5db5937e223e6ffeb855f3f5ade873e18b83d9854978dae869c110</a>',
#     'CREATEDDATE': '2017-08-25T02:28:20.000Z',
#     'FB_SECRET__C': '',
#     'LASTVIEWEDDATE': '',
#     'AD_ACCOUNT_STATUS__C': '',
#     'AD_ACCOUNT_ACTIVE__C': 'true',
#     'STATUS__C': '',
#     'NAME': 'd66098cb5db5937e223e6ffeb855f3f5ade873e18b83d9854978dae869c110',
#     'LOGIN_NOTIFICATIONS_DISABLED__C': 'false',
#     'CREATEDBYID': '00546000000rlLVAAY',
#     'FB_EMAIL__C': '',
#     'IP_ADDRESS__C': '64.233.172.179'
# }