from __future__ import unicode_literals

import calendar
import datetime
from dateutil.relativedelta import relativedelta

from django.utils import timezone
from django.db import models

from adsrental.models.lead_history import LeadHistory
from adsrental.models.mixins import FulltextSearchMixin
from adsrental.models.lead import Lead
from adsrental.models.lead_account import LeadAccount


class LeadHistoryMonth(models.Model, FulltextSearchMixin):
    '''
    Aggregated monthly stats for :model:`adsrental.Lead`.
    Used to calculate payments to leads.
    '''
    class Meta:
        verbose_name = 'Lead History Month'
        verbose_name_plural = 'Lead Histories Month'

    MAX_PAYMENT = 25.
    NEW_MAX_PAYMENT = 15.
    NEW_FACEBOOK_MAX_PAYMENT_DATE = datetime.datetime(2018, 3, 29, tzinfo=timezone.get_default_timezone())
    NEW_GOOGLE_MAX_PAYMENT_DATE = datetime.datetime(2018, 3, 29, tzinfo=timezone.get_default_timezone())

    lead = models.ForeignKey(Lead, help_text='Linked lead.', on_delete=models.CASCADE)
    date = models.DateField(db_index=True)
    days_offline = models.IntegerField(default=0, help_text='Days when device had been online less than 12 hours.')
    days_online = models.IntegerField(default=0, help_text='Days when device had been online more than 12 hours.')
    days_wrong_password = models.IntegerField(default=0, help_text='Days when wrong password was reported at least once.')
    max_payment = models.DecimalField(null=True, blank=True, max_digits=6, decimal_places=2, help_text='Max payment to lead, depends on qualified date and his accounts.')
    amount = models.DecimalField(null=True, blank=True, max_digits=6, decimal_places=2, help_text='Sum to be paid to lead')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def aggregate(self):
        self.days_offline = 0
        self.days_online = 0
        self.days_wrong_password = 0
        lead_histories = LeadHistory.objects.filter(
            lead=self.lead,
            date__gte=self.date.replace(day=1),
            date__lt=self.date + relativedelta(months=1),
        ).prefetch_related(
            'lead',
            'lead__raspberry_pi',
            'lead__lead_accounts',
        )
        for lead_history in lead_histories:
            if lead_history.checks_online and lead_history.checks_online > lead_history.checks_offline:
                self.days_online += 1
                if lead_history.checks_wrong_password:
                    self.days_wrong_password += 1
            else:
                self.days_offline += 1

        self.max_payment = self.get_max_payment()
        self.amount = self.get_amount()
        self.save()

    @classmethod
    def get_or_create(cls, lead, date):
        date_month = date.replace(day=1)
        item = cls.objects.filter(date=date_month, lead=lead).first()
        if item:
            return item

        return cls(lead=lead, date=date_month)

    def get_max_payment(self):
        result = 0.
        raspberry_pi = self.lead.raspberry_pi
        if not raspberry_pi or not raspberry_pi.first_seen:
            return result
        for lead_account in self.lead.lead_accounts.all():
            if not lead_account.active:
                continue
            if lead_account.account_type == LeadAccount.ACCOUNT_TYPE_GOOGLE:
                if raspberry_pi.first_seen > self.NEW_GOOGLE_MAX_PAYMENT_DATE:
                    result += self.NEW_MAX_PAYMENT
                else:
                    result += self.MAX_PAYMENT
            if lead_account.account_type == LeadAccount.ACCOUNT_TYPE_FACEBOOK:
                if raspberry_pi.first_seen > self.NEW_FACEBOOK_MAX_PAYMENT_DATE:
                    result += self.NEW_MAX_PAYMENT
                else:
                    result += self.MAX_PAYMENT

        return result

    def get_amount(self):
        if not self.days_online:
            return 0

        days_in_month = calendar.monthrange(self.date.year, self.date.month)[1]
        days_online_valid = max(self.days_online - self.days_wrong_password, 0)
        max_payment = self.get_max_payment()
        return max_payment * days_online_valid / days_in_month
