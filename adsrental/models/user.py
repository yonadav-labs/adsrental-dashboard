
from __future__ import unicode_literals

import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.contrib.auth.models import BaseUserManager


class User(AbstractBaseUser, PermissionsMixin):
    '''
    Stores a single user models.
    '''
    class Meta:
        app_label = 'adsrental'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255, default='')
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    utm_source = models.CharField(max_length=255, default='', blank=True, help_text='If not NULL, leads in dashboard will be filtered by this utm_source. SHould be changed to bundler.')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    objects = BaseUserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

    def get_short_name(self):
        return self.email

    def get_full_name(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.email:
            self.email = self.username
        if not self.username:
            self.username = self.email
        super(User, self).save(*args, **kwargs)
