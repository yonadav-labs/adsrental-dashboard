from django.db import models


class Lead(models.Model):
    name = models.CharField(max_length=255, db_column='Name', db_index=True)
    title = models.CharField(max_length=255, db_column='Title', null=True, blank=True)
    address = models.CharField(max_length=1024, db_column='Address', null=True, blank=True)
    annual_revenue = models.BigIntegerField(db_column='AnnualRevenue', null=True, blank=True)
    mobile = models.CharField(max_length=255, db_column='MobilePhone', null=True, blank=True)
    phone = models.CharField(max_length=255, db_column='Phone', null=True, blank=True)
    raspberry_pi = models.ForeignKey('adsrental.RaspberryPi', null=True, blank=True)

    google_account = models.BooleanField(db_column='Google_Account__c', default=False)
    google_account_status = models.CharField(max_length=255, db_column='Google_Account_Status__c', null=True, blank=True)
    facebook_account = models.BooleanField(db_column='Facebook_Account__c', default=False)
    facebook_account_status = models.CharField(max_length=255, db_column='Facebook_Account_Status__c', null=True, blank=True)
    facebook_email = models.CharField(max_length=255, db_column='FB_email__c', null=True, blank=True)
    facebook_friends = models.IntegerField(db_column='FB_friends__c', null=True, blank=True)
    facebook_secret = models.CharField(max_length=255, db_column='FB_secret__c', null=True, blank=True)

    def __str__(self):
        return self.name

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
