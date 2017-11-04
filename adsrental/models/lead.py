import string

from django.db import models

from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.models.browser_extension import BrowserExtension


class Lead(models.Model):
    salesforce_id = models.CharField(max_length=255, db_index=True, null=True)
    name = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    jigsaw_contact_id = models.CharField(max_length=255, null=True, blank=True)
    middlename = models.CharField(max_length=255, null=True, blank=True)
    geocode_accuracy = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=255, null=True, blank=True)
    street = models.CharField(max_length=255, null=True, blank=True)
    activation_ip_address = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    activation_isp = models.CharField(max_length=255, null=True, blank=True)
    winprox_download_url = models.CharField(max_length=255, null=True, blank=True)
    account_name = models.CharField(max_length=255, null=True, blank=True)
    ad_account_status_last_checked = models.DateField(null=True, blank=True)
    rating = models.CharField(max_length=255, null=True, blank=True)
    credentials_acquired = models.BooleanField(default=True)
    registered_isp = models.CharField(max_length=255, null=True, blank=True)
    not_banned_status = models.CharField(max_length=255, null=True, blank=True)
    longitude = models.CharField(max_length=255, null=True, blank=True)
    banned_reason = models.CharField(max_length=255, null=True, blank=True)
    old_pi_status = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    industry = models.CharField(max_length=255, null=True, blank=True)
    jigsaw = models.CharField(max_length=255, null=True, blank=True)
    billed = models.BooleanField(default=True)
    lead_source = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    winprox_online = models.BooleanField(default=True)
    lastname = models.CharField(max_length=255, null=True, blank=True)
    facebook_account = models.BooleanField(default=False)
    is_converted = models.BooleanField(default=False)
    winprox_tunnel_last_started = models.DateTimeField(null=True, blank=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    remarks = models.CharField(max_length=255, null=True, blank=True)
    email_bounced_date = models.DateTimeField(null=True, blank=True)
    company = models.CharField(max_length=255, null=True, blank=True)
    converted_account_id = models.CharField(max_length=255, null=True, blank=True)
    payment_first_name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    last_referenced_date = models.DateTimeField(null=True, blank=True)
    secret_changed = models.CharField(max_length=255, null=True, blank=True)
    last_touch_date = models.DateTimeField(null=True, blank=True)
    converted_date = models.DateTimeField(null=True, blank=True)
    winprox_ec2_instance = models.CharField(max_length=255, null=True, blank=True)
    created_date = models.DateTimeField(null=True, blank=True)
    salutation = models.CharField(max_length=255, null=True, blank=True)
    ad_account_status = models.CharField(max_length=255, null=True, blank=True)
    master_record_id = models.CharField(max_length=255, null=True, blank=True)
    firstname = models.CharField(max_length=255, null=True, blank=True)
    photo_url = models.CharField(max_length=255, null=True, blank=True)
    bundler_paid = models.BooleanField(default=False)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    is_unread_by_owner = models.BooleanField(default=False)
    useragent = models.CharField(max_length=255, null=True, blank=True)
    payment_last_name = models.CharField(max_length=255, null=True, blank=True)
    winprox_status = models.CharField(max_length=255, null=True, blank=True)
    suffix = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    last_modified_date = models.DateTimeField(null=True, blank=True)
    payment_zipcode = models.CharField(max_length=255, null=True, blank=True)
    last_modified_by_id = models.CharField(max_length=255, null=True, blank=True)
    touch_count = models.IntegerField(null=True, blank=True)
    facebook_profile_url = models.CharField(max_length=255, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    paspberry_pi_ec2_instance_hostname = models.CharField(max_length=255, null=True, blank=True)
    converted_opportunity_id = models.CharField(max_length=255, null=True, blank=True)
    wrong_password = models.BooleanField(default=False)
    system_mod_stamp = models.DateTimeField(null=True, blank=True)
    winprox_last_seen = models.DateTimeField(null=True, blank=True)
    payment_street = models.CharField(max_length=255, null=True, blank=True)
    payment_state = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    registered_ip_address = models.CharField(max_length=255, null=True, blank=True)
    owner_id = models.CharField(max_length=255, null=True, blank=True)
    fb_secret = models.CharField(max_length=255, null=True, blank=True)
    google_account = models.BooleanField(default=False)
    number_of_employees = models.CharField(max_length=255, null=True, blank=True)
    fb_friends = models.CharField(max_length=255, null=True, blank=True)
    winprox_log_url = models.CharField(max_length=255, null=True, blank=True)
    qualified_lead = models.BooleanField(default=False)
    connection_sent_id = models.CharField(max_length=255, null=True, blank=True)
    payment_city = models.CharField(max_length=255, null=True, blank=True)
    activation_seed = models.CharField(max_length=255, null=True, blank=True)
    facebook_account_status = models.CharField(max_length=255, null=True, blank=True)
    email_bounced_reason = models.CharField(max_length=255, null=True, blank=True)
    google_account_status = models.CharField(max_length=255, null=True, blank=True)
    connection_received_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    mobile_phone = models.CharField(max_length=255, null=True, blank=True)
    last_activity_date = models.DateField(null=True, blank=True)
    latitude = models.CharField(max_length=255, null=True, blank=True)
    dns_anonymization_updated = models.BooleanField(default=False)
    activation_key = models.CharField(max_length=255, null=True, blank=True)
    last_viewed_date = models.DateTimeField(null=True, blank=True)
    utm_source = models.CharField(max_length=255, null=True, blank=True)
    winprox_uid = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    login_notifications_disabled = models.BooleanField(default=False)
    raspberry_pi = models.ForeignKey(RaspberryPi, null=True, blank=True)
    fb_email = models.CharField(max_length=255, null=True, blank=True)
    browser_extension = models.ForeignKey(BrowserExtension, null=True, blank=True)
    browser_extension_installed = models.BooleanField(default=False)
    activation_url = models.CharField(max_length=255, null=True, blank=True)

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
                jigsaw_contact_id=data['JIGSAWCONTACTID'],
                middlename=data['MIDDLENAME'],
                geocode_accuracy=data['GEOCODEACCURACY'],
                postal_code=data['POSTALCODE'],
                street=data['STREET'],
                activation_ip_address=data['ACTIVATION_IP_ADDRESS__C'],
                email=data['EMAIL'],
                activation_isp=data['ACTIVATION_ISP__C'],
                winprox_download_url=data['WINPROX_DOWNLOAD_URL__C'],
                account_name=data['ACCOUNT_NAME__C'],
                ad_account_status_last_checked=data['AD_ACCOUNT_STATUS_LAST_CHECKED__C'] if data['AD_ACCOUNT_STATUS_LAST_CHECKED__C'] else None,
                rating=data['RATING'],
                credentials_acquired=data['CREDENTIALS_ACQUIRED__C'] == 'true',
                registered_isp=data['REGISTERED_ISP__C'],
                not_banned_status=data['NOTBANNEDSTATUS__C'],
                longitude=data['LONGITUDE'],
                banned_reason=data['BANNED_REASON__C'],
                old_pi_status=data['OLD_PI_STATUS__C'],
                country=data['COUNTRY'],
                industry=data['INDUSTRY'],
                jigsaw=data['JIGSAW'],
                billed=data['BILLED__C'] == 'true',
                lead_source=data['LEADSOURCE'],
                address=data['ADDRESS'],
                winprox_online=data['WINPROX_ONLINE__C'] == 'true',
                lastname=data['LASTNAME'],
                facebook_account=data['FACEBOOK_ACCOUNT__C'] == 'true',
                is_converted=data['ISCONVERTED'] == 'true',
                winprox_tunnel_last_started=data['WINPROX_TUNNEL_LAST_STARTED__C'] or None,
                website=data['WEBSITE'],
                remarks=data['REMARKS__C'],
                email_bounced_date=data['EMAILBOUNCEDDATE'] or None,
                company=data['COMPANY'],
                converted_account_id=data['CONVERTEDACCOUNTID'],
                payment_first_name=data['PAYMENT_FIRST_NAME__C'],
                phone=data['PHONE'],
                last_referenced_date=data['LASTREFERENCEDDATE'] or None,
                secret_changed=data['SECRET_CHANGED__C'] == 'true',
                last_touch_date=data['LAST_TOUCH_DATE__C'] or None,
                converted_date=data['CONVERTEDDATE'] or None,
                winprox_ec2_instance=data['WINPROX_EC2_INSTANCE__C'],
                created_date=data['CREATEDDATE'] if data['CREATEDDATE'] else None,
                salutation=data['SALUTATION'],
                ad_account_status=cls.str_printable(data['AD_ACCOUNT_STATUS__C']),
                master_record_id=data['MASTERRECORDID'],
                firstname=cls.str_printable(data['FIRSTNAME']),
                photo_url=data['PHOTOURL'],
                bundler_paid=data['BUNDLER_PAID__C'] == 'true',
                created_by=data['CREATEDBYID'],
                is_unread_by_owner=data['ISUNREADBYOWNER'] == 'true',
                useragent=data['USERAGENT__C'],
                payment_last_name=data['PAYMENT_LAST_NAME__C'],
                winprox_status=data['WINPROX_STATUS__C'],
                suffix=data['SUFFIX'],
                title=data['TITLE'],
                last_modified_date=data['LASTMODIFIEDDATE'] or None,
                payment_zipcode=data['PAYMENT_ZIPCODE__C'],
                last_modified_by_id=data['LASTMODIFIEDBYID'],
                touch_count=data['TOUCH_COUNT__C'].split('.')[0] if data['TOUCH_COUNT__C'] else None,
                facebook_profile_url=data['FACEBOOK_PROFILE_URL__C'],
                is_deleted=data['ISDELETED'] == 'true',
                paspberry_pi_ec2_instance_hostname=data['RASPBERRY_PI_EC2_INSTANCE_HOSTNAME__C'],
                converted_opportunity_id=data['CONVERTEDOPPORTUNITYID'],
                wrong_password=data['WRONG_PASSWORD__C'] == 'true',
                system_mod_stamp=data['SYSTEMMODSTAMP'] or None,
                winprox_last_seen=data['WINPROX_LAST_SEEN__C'] or None,
                payment_street=data['PAYMENT_STREET__C'],
                payment_state=data['PAYMENT_STATE__C'],
                state=data['STATE'],
                registered_ip_address=data['REGISTERED_IP_ADDRESS__C'],
                owner_id=data['OWNERID'],
                fb_secret=data['FB_SECRET__C'],
                google_account=data['GOOGLE_ACCOUNT__C'] == 'true',
                name=cls.str_printable(data['NAME']),
                number_of_employees=data['NUMBEROFEMPLOYEES'],
                fb_friends=data['FB_FRIENDS__C'],
                winprox_log_url=data['WINPROX_LOG_URL__C'],
                qualified_lead=data['QUALIFIED_LEAD__C'] == 'true',
                connection_sent_id=data['CONNECTIONSENTID'],
                payment_city=data['PAYMENT_CITY__C'],
                activation_seed=data['ACTIVATION_SEED_1__C'],
                facebook_account_status=data['FACEBOOK_ACCOUNT_STATUS__C'],
                email_bounced_reason=data['EMAILBOUNCEDREASON'],
                google_account_status=data['GOOGLE_ACCOUNT_STATUS__C'],
                connection_received_id=data['CONNECTIONRECEIVEDID'],
                status=data['STATUS'],
                mobile_phone=data['MOBILEPHONE'],
                last_activity_date=data['LASTACTIVITYDATE'] or None,
                latitude=data['LATITUDE'],
                dns_anonymization_updated=data['DNS_ANONYMIZATION_UPDATED__C'] == 'true',
                activation_key=data['ACTIVATION_KEY__C'],
                last_viewed_date=data['LASTVIEWEDDATE'] or None,
                utm_source=data['UTM_SOURCE__C'],
                winprox_uid=data['WINPROX_UID__C'],
                city=cls.str_printable(data['CITY']),
                login_notifications_disabled=data['LOGIN_NOTIFICATIONS_DISABLED__C'] == 'true',
                raspberry_pi=RaspberryPi.objects.filter(salesforce_id=data['RASPBERRY_PI__C']).first(),
                fb_email=data['FB_EMAIL__C'],
                browser_extension=BrowserExtension.objects.filter(salesforce_id=data['BROWSER_EXTENSION__C']).first(),
                browser_extension_installed=data['BROWSER_EXTENSION_INSTALLED__C'] == 'true',
                activation_url=data['ACTIVATION_URL__C'],
            ),
        )
        item.save()

# {
#     'JIGSAWCONTACTID': '',
#     'MIDDLENAME': '',
#     'GEOCODEACCURACY': '',
#     'POSTALCODE': '77055',
#     'STREET': '456 Main St',
#     'ACTIVATION_IP_ADDRESS__C': '73.166.155.174',
#     'EMAIL': '',
#     'ACTIVATION_ISP__C': '',
#     'WINPROX_DOWNLOAD_URL__C': '<a href="https://adsrental.com/download.php?uid=3f5aa3f960c6d292a1d959d26c1175b2" target="_blank">https://adsrental.com/download.php?uid=3f5aa3f960c6d292a1d959d26c1175b2</a>',
#     'ACCOUNT_NAME__C': '',
#     'AD_ACCOUNT_STATUS_LAST_CHECKED__C': '',
#     'RATING': '',
#     'CREDENTIALS_ACQUIRED__C': 'false',
#     'REGISTERED_ISP__C': 'Comcast Cable',
#     'NOTBANNEDSTATUS__C': '',
#     'LONGITUDE': '',
#     'BANNED_REASON__C': '',
#     'OLD_PI_STATUS__C': 'Offline',
#     'COUNTRY': 'United States (US)',
#     'INDUSTRY': '',
#     'JIGSAW': '',
#     'BILLED__C': 'false',
#     'LEADSOURCE': 'Website',
#     'ADDRESS': '',
#     'WINPROX_ONLINE__C': 'false',
#     'LASTNAME': 'McGee',
#     'FACEBOOK_ACCOUNT__C': 'true',
#     'ISCONVERTED': 'false',
#     'WINPROX_TUNNEL_LAST_STARTED__C': '',
#     'WEBSITE': '',
#     'REMARKS__C': '',
#     'EMAILBOUNCEDDATE': '',
#     'COMPANY': '[Empty]',
#     'CONVERTEDACCOUNTID': '',
#     'PAYMENT_FIRST_NAME__C': '',
#     'PHONE': '',
#     'CONVERTEDCONTACTID': '',
#     'LASTREFERENCEDDATE': '',
#     'SECRET_CHANGED__C': 'false',
#     'LAST_TOUCH_DATE__C': '',
#     'CONVERTEDDATE': '',
#     'WINPROX_EC2_INSTANCE__C': '',
#     'CREATEDDATE': '2017-05-17T17:40:35.000Z',
#     'SALUTATION': 'Mr.',
#     'AD_ACCOUNT_STATUS__C': '',
#     'MASTERRECORDID': '',
#     'FIRSTNAME': 'Test',
#     'PHOTOURL': '/services/images/photo/00Q46000003r2pAEAQ',
#     'BUNDLER_PAID__C': 'false',
#     'CREATEDBYID': '00546000000rlLVAAY',
#     'ISUNREADBYOWNER': 'false',
#     'USERAGENT__C': '',
#     'PAYMENT_LAST_NAME__C': '',
#     'WINPROX_STATUS__C': '',
#     'SUFFIX': '',
#     'TITLE': '',
#     'LASTMODIFIEDDATE': '2017-09-07T23:03:40.000Z',
#     'PAYMENT_ZIPCODE__C': '',
#     'LASTMODIFIEDBYID': '00546000000rlLVAAY',
#     'TOUCH_COUNT__C': '0.0',
#     'FACEBOOK_PROFILE_URL__C': '',
#     'ISDELETED': 'false',
#     'RASPBERRY_PI_EC2_INSTANCE_HOSTNAME__C': '',
#     'CONVERTEDOPPORTUNITYID': '',
#     'ID': '00Q46000003r2pAEAQ',
#     'WRONG_PASSWORD__C': 'false',
#     'SYSTEMMODSTAMP': '2017-10-13T10:38:03.000Z',
#     'WINPROX_LAST_SEEN__C': '',
#     'PAYMENT_STREET__C': '',
#     'PAYMENT_STATE__C': '',
#     'STATE': 'Texas (TX)',
#     'REGISTERED_IP_ADDRESS__C': '73.166.155.174',
#     'OWNERID': '00546000000rlLVAAY',
#     'FB_SECRET__C': '',
#     'GOOGLE_ACCOUNT__C': 'false',
#     'NAME': 'Test McGee',
#     'NUMBEROFEMPLOYEES': '',
#     'FB_FRIENDS__C': '0.0',
#     'WINPROX_LOG_URL__C': '<a href="https://adsrental.com/log/3f5aa3f960c6d292a1d959d26c1175b2" target="_blank">https://adsrental.com/log/3f5aa3f960c6d292a1d959d26c1175b2</a>',
#     'QUALIFIED_LEAD__C': 'false',
#     'CONNECTIONSENTID': '',
#     'PAYMENT_CITY__C': '',
#     'ACTIVATION_SEED_1__C': '',
#     'FACEBOOK_ACCOUNT_STATUS__C': '',
#     'EMAILBOUNCEDREASON': '',
#     'GOOGLE_ACCOUNT_STATUS__C': '',
#     'CONNECTIONRECEIVEDID': '',
#     'STATUS': 'In-Progress',
#     'MOBILEPHONE': '',
#     'LASTACTIVITYDATE': '',
#     'LATITUDE': '',
#     'DNS_ANONYMIZATION_UPDATED__C': 'false',
#     'ACTIVATION_KEY__C': '',
#     'LASTVIEWEDDATE': '',
#     'UTM_SOURCE__C': '',
#     'WINPROX_UID__C': '3f5aa3f960c6d292a1d959d26c1175b2',
#     'CITY': 'Houston',
#     'LOGIN_NOTIFICATIONS_DISABLED__C': 'false',
#     'RASPBERRY_PI__C': 'a0246000001uLhzAAE',
#     'FB_EMAIL__C': '',
#     'BROWSER_EXTENSION__C': '',
#     'BROWSER_EXTENSION_INSTALLED__C': 'false',
#     'ACTIVATION_URL__C': '<a href="https://adsrental.com/check.html?" target="_blank">https://adsrental.com/check.html?</a>'
# }
