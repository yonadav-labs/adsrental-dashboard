from __future__ import unicode_literals

from django.db import models


class Bundler(models.Model):
    '''
    Stores a single bundler entry, used to get bundler info for lead by *utm_source*
    '''
    name = models.CharField(max_length=255, unique=True, db_index=True)
    utm_source = models.CharField(max_length=50, db_index=True, null=True, blank=True)
    adsdb_id = models.IntegerField(null=True, blank=True, help_text='ID from adsdb database')
    email = models.CharField(max_length=255, null=True, blank=True)
    skype = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    bank_info = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True, help_text='If inactive, landing/sugnup page will not be shown for this utm_source.')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @classmethod
    def get_by_utm_source(cls, utm_source):
        return cls.objects.filter(utm_source=utm_source).first()

    @classmethod
    def get_by_adsdb_id(cls, adsdb_id):
        return cls.objects.filter(adsdb_id=adsdb_id).first()

    def __str__(self):
        return self.name
        # return '{} ({})'.format(self.name, self.utm_source)
