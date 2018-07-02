import datetime
import decimal

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

    MAX_PAYMENT = decimal.Decimal('25.00')
    NEW_MAX_PAYMENT = decimal.Decimal('15.00')
    AMAZON_MAX_PAYMENT = decimal.Decimal('10.00')
    NEW_FACEBOOK_MAX_PAYMENT_DATE = datetime.datetime(2018, 3, 19, tzinfo=timezone.get_default_timezone())
    NEW_GOOGLE_MAX_PAYMENT_DATE = datetime.datetime(2018, 3, 29, tzinfo=timezone.get_default_timezone())

    lead = models.ForeignKey(Lead, help_text='Linked lead.', on_delete=models.CASCADE)
    date = models.DateField(db_index=True)
    days_offline = models.IntegerField(default=0, help_text='Days when device had been online less than 12 hours.')
    days_online = models.IntegerField(default=0, help_text='Days when device had been online more than 12 hours.')
    days_wrong_password = models.IntegerField(default=0, help_text='Days when wrong password was reported at least once.')
    max_payment = models.DecimalField(null=True, blank=True, max_digits=6, decimal_places=2, help_text='Max payment to lead, depends on qualified date and his accounts.')
    amount = models.DecimalField(default=decimal.Decimal('0.00'), max_digits=6, decimal_places=2, help_text='Sum to be paid to lead')
    amount_paid = models.DecimalField(default=decimal.Decimal('0.00'), max_digits=6, decimal_places=2, help_text='Sum paid tot lead')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def aggregate(self):
        self.days_offline = 0
        self.days_online = 0
        self.days_wrong_password = 0
        lead_histories = LeadHistory.objects.filter(
            lead=self.lead,
            date__gte=self.get_first_day(),
            date__lte=self.get_last_day(),
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

    @classmethod
    def get_or_create(cls, lead, date):
        date_month = date.replace(day=1)
        item = cls.objects.filter(date=date_month, lead=lead).first()
        if item:
            return item

        return cls(lead=lead, date=date_month)

    def get_max_payment(self):
        result = decimal.Decimal('0.00')
        raspberry_pi = self.lead.raspberry_pi
        if not raspberry_pi or not raspberry_pi.first_seen:
            return result
        for lead_account in self.lead.lead_accounts.all():
            if not lead_account.active:
                continue

            created_date = lead_account.created
            if created_date.date() > self.get_last_day():
                continue

            coef = decimal.Decimal('1.00')
            if created_date.date() > self.get_first_day():
                days_in_month = (self.get_last_day() - self.get_first_day()).days
                registered_days = (created_date.date() - self.get_first_day()).days + 1
                coef = decimal.Decimal(registered_days / days_in_month)

            if lead_account.account_type == LeadAccount.ACCOUNT_TYPE_GOOGLE:
                if created_date > self.NEW_GOOGLE_MAX_PAYMENT_DATE:
                    result += self.NEW_MAX_PAYMENT * coef
                else:
                    result += self.MAX_PAYMENT * coef
            if lead_account.account_type == LeadAccount.ACCOUNT_TYPE_FACEBOOK:
                if created_date > self.NEW_FACEBOOK_MAX_PAYMENT_DATE:
                    result += self.NEW_MAX_PAYMENT * coef
                else:
                    result += self.MAX_PAYMENT * coef
            if lead_account.account_type == LeadAccount.ACCOUNT_TYPE_AMAZON:
                result += self.AMAZON_MAX_PAYMENT * coef

        return result

    def get_last_day(self):
        next_month = self.date.replace(day=28) + datetime.timedelta(days=4)
        return next_month - datetime.timedelta(days=next_month.day)

    def get_first_day(self):
        return self.date.replace(day=1)

    def get_amount(self):
        if not self.days_online:
            return decimal.Decimal('0.00')

        days_in_month = (self.get_last_day() - self.get_first_day()).days + 1
        days_online_valid = max(self.days_online - self.days_wrong_password, 0)
        max_payment = self.get_max_payment()
        return round(max_payment * days_online_valid / days_in_month, 2)

    def get_remaining_amount(self):
        return self.amount - self.amount_paid
