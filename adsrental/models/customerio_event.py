from __future__ import unicode_literals

from django.db import models

from adsrental.models.mixins import FulltextSearchMixin


class CustomerIOEvent(models.Model, FulltextSearchMixin):
    '''
    Stores a single event for CustomerIO entry. Related to :model:`adsrental.Lead`.
    '''
    NAME_SHIPPED = 'shipped'
    NAME_DELIVERED = 'delivered'
    NAME_OFFLINE = 'offline'
    NAME_APPROVED = 'lead_approved'
    NAME_BANNED = 'banned'
    NAME_AVAILABLE_BANNED = 'available_banned'
    NAME_CHOICES = [
        (NAME_SHIPPED, 'Shipped'),
        (NAME_DELIVERED, 'Delivered'),
        (NAME_OFFLINE, 'Offline'),
        (NAME_APPROVED, 'Approved'),
        (NAME_BANNED, 'Banned'),
        (NAME_AVAILABLE_BANNED, 'Banned from available status'),
    ]

    lead = models.ForeignKey('adsrental.Lead', null=True, blank=True, default=None, help_text='Linked lead.', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, choices=NAME_CHOICES, help_text='Event name. Used in customer.io filters.')
    kwargs = models.TextField(blank=True, null=True, help_text='Extra data sent to event, like hours_offline')
    sent = models.BooleanField(default=True, help_text='Is published to customer.io or not.')
    created = models.DateTimeField(auto_now_add=True)
