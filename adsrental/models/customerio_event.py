from __future__ import unicode_literals

from django.db import models

from adsrental.models.mixins import FulltextSearchMixin


class CustomerIOEvent(models.Model, FulltextSearchMixin):
    NAME_SHIPPED = 'shipped'
    NAME_DELIVERED = 'delivered'
    NAME_OFFLINE = 'offline'
    NAME_APPROVED = 'lead_approved'
    NAME_CHOICES = [
        (NAME_SHIPPED, 'Shipped'),
        (NAME_DELIVERED, 'Delivered'),
        (NAME_OFFLINE, 'Offline'),
        (NAME_APPROVED, 'Approved'),
    ]

    lead = models.ForeignKey('adsrental.Lead', null=True, blank=True, default=None)
    name = models.CharField(max_length=255, choices=NAME_CHOICES)
    kwargs = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
