from __future__ import unicode_literals

from django.db import models
from django.utils import timezone


class RaspberryPiSession(models.Model):
    raspberry_pi = models.ForeignKey('adsrental.RaspberryPi')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    @classmethod
    def start(cls, raspberry_pi):
        return cls(raspberry_pi=raspberry_pi).save()

    @classmethod
    def end(cls, raspberry_pi):
        return cls.objects.filter(raspberry_pi=raspberry_pi, end_date__isnull=True).update(end_date=timezone.now())
