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
