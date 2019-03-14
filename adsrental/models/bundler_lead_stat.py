from __future__ import annotations

import datetime
import typing

from django.db import models
from django.apps import apps
from django.utils import timezone


if typing.TYPE_CHECKING:
    from adsrental.models.bundler import Bundler


class BundlerLeadStat(models.Model):
    bundler = models.ForeignKey('Bundler', on_delete=models.deletion.CASCADE)
    in_progress_total = models.IntegerField(default=0)
    in_progress_offline = models.IntegerField(default=0)
    in_progress_wrong_pw = models.IntegerField(default=0)
    in_progress_security_checkpoint = models.IntegerField(default=0)
    in_progress_total_issue = models.IntegerField(default=0)
    autobans_last_30_days = models.IntegerField(default=0)
    autobans_total = models.IntegerField(default=0)
    bans_last_30_days = models.IntegerField(default=0)
    bans_total = models.IntegerField(default=0)
    qualified_today = models.IntegerField(default=0)
    qualified_yesterday = models.IntegerField(default=0)
    qualified_last_30_days = models.IntegerField(default=0)
    qualified_total = models.IntegerField(default=0)
    delivered_not_connected = models.IntegerField(default=0)
    delivered_not_connected_last_30_days = models.IntegerField(default=0)
    delivered_last_30_days = models.IntegerField(default=0)
    delivered_last_14_days = models.IntegerField(default=0)
    delivered_not_connected_last_14_days = models.IntegerField(default=0)
    banned_from_qualified_last_30_days = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.bundler.name

    @classmethod
    def calculate(cls, bundler: Bundler) -> None:
        obj = cls(bundler=bundler)
        LeadAccount = apps.get_model('adsrental', 'LeadAccount')
        lead_accounts = LeadAccount.objects.filter(lead__bundler=obj.bundler, account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK).prefetch_related('lead', 'lead__raspberry_pi')
        now = timezone.localtime(timezone.now())
        last_30_days_start = now - datetime.timedelta(days=30)
        last_14_days_start = now - datetime.timedelta(days=14)
        delivered_last_14_days_lead_accounts = lead_accounts.filter(
            lead__delivery_date__lte=now - datetime.timedelta(days=2),
            lead__delivery_date__gte=last_14_days_start,
        ).exclude(
            status=LeadAccount.STATUS_AVAILABLE,
        )
        obj.delivered_last_14_days = delivered_last_14_days_lead_accounts.count()
        obj.delivered_not_connected_last_14_days = delivered_last_14_days_lead_accounts.filter(
            in_progress_date__isnull=True,
        ).count()
        for lead_account in lead_accounts:
            lead = lead_account.lead
            raspberry_pi = lead.raspberry_pi
            if lead_account.status == LeadAccount.STATUS_IN_PROGRESS:
                obj.in_progress_total += 1
                if lead_account.is_wrong_password():
                    obj.in_progress_wrong_pw += 1
                if lead_account.is_security_checkpoint_reported():
                    obj.in_progress_security_checkpoint += 1
                if raspberry_pi:
                    if not raspberry_pi.online():
                        obj.in_progress_offline += 1
                    if not raspberry_pi.online() or lead_account.is_wrong_password() or lead_account.is_security_checkpoint_reported():
                        obj.in_progress_total_issue += 1

            if lead_account.ban_reason:
                if lead_account.ban_reason in LeadAccount.AUTO_BAN_REASONS:
                    obj.autobans_total += 1
                    if lead_account.banned_date and lead_account.banned_date > last_30_days_start:
                        obj.autobans_last_30_days += 1

                obj.bans_total += 1
                if lead_account.banned_date and lead_account.banned_date > last_30_days_start:
                    obj.bans_last_30_days += 1

            if lead_account.qualified_date:
                obj.qualified_total += 1
                if lead_account.qualified_date > now.replace(hour=0, minute=0, second=0):
                    obj.qualified_today += 1
                elif lead_account.qualified_date > now.replace(hour=0, minute=0, second=0) - datetime.timedelta(days=1):
                    obj.qualified_yesterday += 1

        cls.objects.filter(bundler=bundler).delete()
        obj.save()
