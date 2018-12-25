from __future__ import annotations

import typing

from django.db import models
from django.utils import timezone


if typing.TYPE_CHECKING:
    from adsrental.models.raspberry_pi import RaspberryPi


class RaspberryPiSession(models.Model):
    '''
    Created every time :model:`adsrental.RaspberryPi` comes online. CLosed when it comes offline.
    Will be potentially used in stats calculation and test sessions.
    '''
    raspberry_pi = models.ForeignKey('adsrental.RaspberryPi', on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    test = models.BooleanField(default=False)
    end_date = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    @classmethod
    def start(cls, raspberry_pi: RaspberryPi, test: bool = False) -> RaspberryPiSession:
        return cls(raspberry_pi=raspberry_pi, test=test).save()

    @classmethod
    def end(cls, raspberry_pi: RaspberryPi) -> typing.Union[models.query.QuerySet, typing.List[RaspberryPiSession]]:
        return cls.objects.filter(raspberry_pi=raspberry_pi, end_date__isnull=True).update(end_date=timezone.now())
