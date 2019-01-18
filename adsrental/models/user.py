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
    utm_source = models.CharField(max_length=255, default='', blank=True, help_text='Obsolete')
    allowed_raspberry_pis = models.ManyToManyField('RaspberryPi', blank=True)
    bundler = models.ForeignKey('adsrental.Bundler', null=True, blank=True, on_delete=models.SET_NULL, help_text='If not NULL, leads in dashboard will be filtered by this bundler.utm_source.')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    objects = BaseUserManager()

    USERNAME_FIELD = 'email'

    def __str__(self) -> str:
        return self.get_full_name()

    def get_short_name(self) -> str:
        return f'{self.first_name}'

    def get_full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'

    def save(self, *args: str, **kwargs: str) -> None:
        if not self.email:
            self.email = self.username
        if not self.username:
            self.username = self.email
        super(User, self).save(*args, **kwargs)

    def is_bookkeeper(self) -> bool:
        return self.groups.filter(name='Bookkeeper').exists()
