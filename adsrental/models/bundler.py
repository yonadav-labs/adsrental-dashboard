from __future__ import unicode_literals

from django.db import models


class Bundler(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    utm_source = models.CharField(max_length=255, db_index=True)
    adsdb_id = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @classmethod
    def get_by_utm_source(cls, utm_source):
        utm_source_digits = ''.join([i for i in utm_source if i.isdigit()])
        if not utm_source_digits:
            return None
        return cls.objects.filter(utm_source=int(utm_source_digits)).first()

    def __str__(self):
        return '{} ({})'.format(self.utm_source, self.name)
