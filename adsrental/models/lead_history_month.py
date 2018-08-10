import datetime
import decimal

from django.utils import timezone
from django.conf import settings
from django.db import models
from django_bulk_update.manager import BulkUpdateManager
from django_bulk_update.helper import bulk_update

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
    MOVE_AMOUNT = decimal.Decimal('5.00')
    NEW_FACEBOOK_MAX_PAYMENT_DATE = datetime.datetime(2018, 3, 19, tzinfo=timezone.get_default_timezone())
    NEW_GOOGLE_MAX_PAYMENT_DATE = datetime.datetime(2018, 3, 29, tzinfo=timezone.get_default_timezone())

    lead = models.ForeignKey(Lead, help_text='Linked lead.', on_delete=models.CASCADE)
    date = models.DateField(db_index=True)
    days_offline = models.IntegerField(default=0, help_text='Days when device had been online less than 3 hours.')
    days_online = models.IntegerField(default=0, help_text='Days when device had been online more than 3 hours.')
    days_wrong_password = models.IntegerField(default=0, help_text='Days when wrong password was reported at least 3 hours.')
    days_sec_checkpoint = models.IntegerField(default=0, help_text='Days when security checkpoint was reported at least 3 hours.')
    max_payment = models.DecimalField(null=True, blank=True, max_digits=6, decimal_places=2, help_text='Max payment to lead, depends on qualified date and his accounts.')
    amount = models.DecimalField(default=decimal.Decimal('0.00'), max_digits=6, decimal_places=2, help_text='Sum to be paid to lead')
    amount_moved = models.DecimalField(default=decimal.Decimal('0.00'), max_digits=6, decimal_places=2, help_text='Amount moved from next month')
    amount_paid = models.DecimalField(default=decimal.Decimal('0.00'), max_digits=6, decimal_places=2, help_text='Sum paid tot lead')
    note = models.TextField(blank=True, null=True, help_text='Note about payment calc')
    move_to_next_month = models.BooleanField(default=False)
    check_number = models.IntegerField(default=None, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = BulkUpdateManager()

    def aggregate(self):
        self.days_offline = 0
        self.days_online = 0
        self.days_wrong_password = 0
        self.days_sec_checkpoint = 0
        lead_histories = LeadHistory.objects.filter(
            lead=self.lead,
            date__gte=self.get_first_day(),
            date__lte=self.get_last_day(),
        ).prefetch_related(
            'lead',
            'lead__raspberry_pi',
            'lead__lead_accounts',
        )

        total_amount = decimal.Decimal('0.00')
        for lead_history in lead_histories:
            amount, note = lead_history.get_amount_with_note()
            lead_history.amount = amount
            lead_history.note = note
            total_amount += amount
            if lead_history.is_wrong_password():
                self.days_wrong_password += 1
            if lead_history.is_sec_checkpoint():
                self.days_sec_checkpoint += 1
            if lead_history.is_online():
                self.days_online += 1
            else:
                self.days_offline += 1

        bulk_update(lead_histories, update_fields=['amount', 'note'])

        self.amount = total_amount

        prev_history = LeadHistoryMonth.objects.filter(lead=self.lead).order_by('-date').first()
        if prev_history and prev_history.move_to_next_month:
            self.amount += prev_history.amount
            self.amount_moved = prev_history.amount

        if self.amount < self.MOVE_AMOUNT:
            self.move_to_next_month = True

    @classmethod
    def get_or_create(cls, lead, date):
        date_month = date.replace(day=1)
        item = cls.objects.filter(date=date_month, lead=lead).first()
        if item:
            return item

        return cls(lead=lead, date=date_month)

    def get_max_payment_with_note(self):
        result = decimal.Decimal('0.00')
        raspberry_pi = self.lead.raspberry_pi

        note = []
        if not raspberry_pi or not raspberry_pi.first_seen:
            return result, 'RaspberryPi does not exist or is not active ($0.00)'
        for lead_account in self.lead.lead_accounts.filter(qualified_date__isnull=False, active=True):
            created_date = lead_account.created
            if lead_account.is_banned():
                note.append('{type} account was banned on {date} ($0.00)'.format(
                    type=lead_account.get_account_type_display(),
                    date=lead_account.banned_date.strftime(settings.HUMAN_DATE_FORMAT) if lead_account.banned_date else 'unknown date',
                ))
                continue

            if created_date.date() > self.get_last_day():
                note.append('{type} account was created only on {date} ($0.00)'.format(
                    type=lead_account.get_account_type_display(),
                    date=lead_account.created.strftime(settings.HUMAN_DATE_FORMAT),
                ))
                continue

            coef = decimal.Decimal('1.00')
            if created_date.date() > self.get_first_day():
                days_in_month = (self.get_last_day() - self.get_first_day()).days + 1
                registered_days = (self.get_last_day() - created_date.date()).days + 1
                coef = decimal.Decimal(registered_days / days_in_month)

            base_payment = decimal.Decimal('0.00')

            if lead_account.account_type == LeadAccount.ACCOUNT_TYPE_GOOGLE:
                if created_date > self.NEW_GOOGLE_MAX_PAYMENT_DATE:
                    base_payment = self.NEW_MAX_PAYMENT
                else:
                    base_payment = self.MAX_PAYMENT
            if lead_account.account_type == LeadAccount.ACCOUNT_TYPE_FACEBOOK:
                if created_date > self.NEW_FACEBOOK_MAX_PAYMENT_DATE:
                    base_payment = self.NEW_MAX_PAYMENT
                else:
                    base_payment = self.MAX_PAYMENT
            if lead_account.account_type == LeadAccount.ACCOUNT_TYPE_AMAZON:
                base_payment = self.AMAZON_MAX_PAYMENT

            result += base_payment * coef
            note.append('{type} account created on {date} (${base} * {coef} = ${result})'.format(
                type=lead_account.get_account_type_display(),
                date=lead_account.created.strftime(settings.HUMAN_DATE_FORMAT),
                base=base_payment,
                coef=round(coef, 2),
                result=round(base_payment * coef, 2),
            ))

        note.append('Total: ${result}'.format(
            result=round(result, 2),
        ))
        return result, '\n'.join(note)

    def get_last_day(self):
        next_month = self.date.replace(day=28) + datetime.timedelta(days=4)
        return next_month - datetime.timedelta(days=next_month.day)

    def get_first_day(self):
        return self.date.replace(day=1)

    def get_amount(self):
        if not self.days_online:
            return decimal.Decimal('0.00')

        days_total = self.days_online + self.days_offline
        days_online_valid = max(self.days_online - self.days_wrong_password, 0)
        return round(self.max_payment * days_online_valid / days_total, 2)

    def get_remaining_amount(self):
        return self.amount - self.amount_paid
