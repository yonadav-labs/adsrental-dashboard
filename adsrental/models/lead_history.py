'LeadHistory class'
import datetime
from dateutil.relativedelta import relativedelta

from django.db import models
from django.utils import timezone
from adsrental.models.lead import Lead
from adsrental.models.lead_account import LeadAccount


class LeadHistory(models.Model):
    '''
    Aggregated daily stats for :model:`adsrental.Lead`.
    Used to calculate payments to leads.
    '''
    ONLINE_CHECKS_MIN = 12
    WRONG_PASSWORD_CHECKS_MIN = 1

    MAX_PAYMENT = 25.
    NEW_MAX_PAYMENT = 15.
    AMAZON_MAX_PAYMENT = 10.
    NEW_FACEBOOK_MAX_PAYMENT_DATE = datetime.datetime(2018, 3, 19, tzinfo=timezone.get_default_timezone())
    NEW_GOOGLE_MAX_PAYMENT_DATE = datetime.datetime(2018, 3, 29, tzinfo=timezone.get_default_timezone())

    class Meta:
        verbose_name = 'Lead History'
        verbose_name_plural = 'Lead Histories'

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    date = models.DateField(db_index=True)
    checks_offline = models.IntegerField(default=0)
    checks_online = models.IntegerField(default=0)
    checks_wrong_password = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def check_lead(self):
        'Update stats for this entry'
        if not self.lead.is_active():
            self.checks_offline += 1
            return

        if self.lead.raspberry_pi.online():
            self.checks_online += 1
        else:
            self.checks_offline += 1

        if self.lead.is_wrong_password():
            self.checks_wrong_password += 1

    @classmethod
    def upsert_for_lead(cls, lead):
        'Create or update stats for this entry'
        today = datetime.date.today()
        lead_history = cls.objects.filter(lead=lead, date=today).first()
        if not lead_history:
            lead_history = cls(lead=lead, date=today)

        lead_history.check_lead()
        lead_history.save()

    def is_online(self):
        'Check iff device was online for more than 12 checks.'
        return self.checks_online > self.ONLINE_CHECKS_MIN

    def is_active(self):
        'Check password was not reported as wrong and device was online'
        return not self.is_wrong_password() and self.is_online()

    def is_wrong_password(self):
        'Check if password for this day was reported wrong at lead once.'
        return self.checks_wrong_password > self.WRONG_PASSWORD_CHECKS_MIN

    @classmethod
    def get_queryset_for_month(cls, year, month, lead_ids=None):
        'Get all entries for given year and month'
        date__gte = datetime.date(year, month, 1)
        date__lt = datetime.date(year, month, 1) + relativedelta(months=1)
        result = cls.objects.filter(date__gte=date__gte, date__lt=date__lt)
        if lead_ids:
            result = result.filter(lead_id__in=lead_ids)
        return result

    def get_last_day(self):
        next_month = self.date.replace(day=28) + datetime.timedelta(days=4)
        return next_month - datetime.timedelta(days=next_month.day)

    def get_first_day(self):
        return self.date.replace(day=1)

    def get_amount(self):
        result = 0.
        if not self.is_online() or self.is_wrong_password():
            return result

        monthly_amount = self.get_monthly_amount()
        days_in_month = (self.get_last_day() - self.get_first_day()).days + 1
        return round(monthly_amount / days_in_month, 2)

    def get_monthly_amount(self):
        result = 0.0
        for lead_account in self.lead.lead_accounts.all():
            if not lead_account.active:
                continue

            created_date = lead_account.created
            if lead_account.account_type == LeadAccount.ACCOUNT_TYPE_GOOGLE:
                if created_date > self.NEW_GOOGLE_MAX_PAYMENT_DATE:
                    result += self.NEW_MAX_PAYMENT
                else:
                    result += self.MAX_PAYMENT
            if lead_account.account_type == LeadAccount.ACCOUNT_TYPE_FACEBOOK:
                if created_date > self.NEW_FACEBOOK_MAX_PAYMENT_DATE:
                    result += self.NEW_MAX_PAYMENT
                else:
                    result += self.MAX_PAYMENT
            if lead_account.account_type == LeadAccount.ACCOUNT_TYPE_AMAZON:
                result += self.AMAZON_MAX_PAYMENT

        return result
