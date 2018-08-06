'LeadHistory class'
import datetime
import decimal
from dateutil.relativedelta import relativedelta

from django.db import models
from django.conf import settings
from django.utils import timezone
from django_bulk_update.manager import BulkUpdateManager

from adsrental.models.lead import Lead
from adsrental.models.lead_account import LeadAccount


class LeadHistory(models.Model):
    '''
    Aggregated daily stats for :model:`adsrental.Lead`.
    Used to calculate payments to leads.
    '''
    ONLINE_CHECKS_MIN = 3
    WRONG_PASSWORD_CHECKS_MIN = 21
    SEC_CHECKPOINT_CHECKS_MIN = 21

    MAX_PAYMENT = decimal.Decimal('25.00')
    NEW_MAX_PAYMENT = decimal.Decimal('15.00')
    AMAZON_MAX_PAYMENT = decimal.Decimal('10.00')
    NEW_FACEBOOK_MAX_PAYMENT_DATE = datetime.datetime(2018, 3, 19, tzinfo=timezone.get_default_timezone())
    NEW_GOOGLE_MAX_PAYMENT_DATE = datetime.datetime(2018, 3, 29, tzinfo=timezone.get_default_timezone())

    class Meta:
        verbose_name = 'Lead Timestamp'
        verbose_name_plural = 'Lead Timestamps'

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    date = models.DateField(db_index=True)
    checks_offline = models.IntegerField(default=0)
    checks_online = models.IntegerField(default=0)
    checks_wrong_password = models.IntegerField(default=0)
    checks_wrong_password_facebook = models.IntegerField(default=0)
    checks_wrong_password_google = models.IntegerField(default=0)
    checks_wrong_password_amazon = models.IntegerField(default=0)
    checks_sec_checkpoint_facebook = models.IntegerField(default=0)
    checks_sec_checkpoint_google = models.IntegerField(default=0)
    checks_sec_checkpoint_amazon = models.IntegerField(default=0)
    amount = models.DecimalField(default=decimal.Decimal('0.00'), max_digits=8, decimal_places=4, help_text='Sum to be paid to lead')
    note = models.TextField(blank=True, null=True, help_text='Note about payment calc')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = BulkUpdateManager()

    def check_lead(self):
        'Update stats for this entry'
        if not self.lead.is_active():
            self.checks_offline += 1
            return

        if self.lead.raspberry_pi.online():
            self.checks_online += 1
        else:
            self.checks_offline += 1

        for lead_account in self.lead.lead_accounts.all():
            if lead_account.wrong_password_date:
                if lead_account.account_type == LeadAccount.ACCOUNT_TYPE_GOOGLE:
                    self.checks_wrong_password_google += 1
                    self.checks_wrong_password += 1
                if lead_account.account_type == LeadAccount.ACCOUNT_TYPE_FACEBOOK:
                    self.checks_wrong_password_facebook += 1
                    self.checks_wrong_password += 1
                if lead_account.account_type == LeadAccount.ACCOUNT_TYPE_AMAZON:
                    self.checks_wrong_password_amazon += 1
                    self.checks_wrong_password += 1
            if lead_account.security_checkpoint_date:
                if lead_account.account_type == LeadAccount.ACCOUNT_TYPE_GOOGLE:
                    self.checks_sec_checkpoint_google += 1
                if lead_account.account_type == LeadAccount.ACCOUNT_TYPE_FACEBOOK:
                    self.checks_sec_checkpoint_facebook += 1
                if lead_account.account_type == LeadAccount.ACCOUNT_TYPE_AMAZON:
                    self.checks_sec_checkpoint_amazon += 1

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
        'Check if password for this day was reported wrong at least 3 times.'
        if self.checks_wrong_password_facebook >= self.WRONG_PASSWORD_CHECKS_MIN:
            return True
        if self.checks_wrong_password_google >= self.WRONG_PASSWORD_CHECKS_MIN:
            return True
        if self.checks_wrong_password_amazon >= self.WRONG_PASSWORD_CHECKS_MIN:
            return True

        return False

    def is_sec_checkpoint(self):
        'Check if security checkpoint for this day was reported at least 3 times.'
        if self.checks_sec_checkpoint_facebook >= self.SEC_CHECKPOINT_CHECKS_MIN:
            return True
        if self.checks_sec_checkpoint_google >= self.SEC_CHECKPOINT_CHECKS_MIN:
            return True
        if self.checks_sec_checkpoint_amazon >= self.SEC_CHECKPOINT_CHECKS_MIN:
            return True

        return False

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

    def get_amount_with_note(self):
        result = decimal.Decimal('0.00')
        if not self.is_online():
            return result, 'Account is offline (${})'.format(result)

        raspberry_pi = self.lead.raspberry_pi
        if not raspberry_pi or not raspberry_pi.first_seen:
            return result, 'RaspberryPi does not exist or is not active (${})'.format(result)

        days_in_month = (self.get_last_day() - self.get_first_day()).days + 1
        note = []
        for lead_account in self.lead.lead_accounts.filter(active=True):
            created_date = lead_account.created.date()
            if created_date > self.date:
                note.append('{type} account was created only on {date} ($0.00)'.format(
                    type=lead_account.get_account_type_display(),
                    date=lead_account.created.strftime(settings.HUMAN_DATE_FORMAT),
                ))
                continue
            if lead_account.is_banned() and (not lead_account.banned_date or lead_account.banned_date.date() <= self.get_last_day()):
                note.append('{type} account was banned on {date} ($0.00)'.format(
                    type=lead_account.get_account_type_display(),
                    date=lead_account.banned_date.strftime(settings.HUMAN_DATE_FORMAT) if lead_account.banned_date else 'unknown date',
                ))
                continue

            if lead_account.account_type == LeadAccount.ACCOUNT_TYPE_GOOGLE:
                checks_wrong_password = self.checks_wrong_password_google
                checks_sec_checkpoint = self.checks_sec_checkpoint_google
            if lead_account.account_type == LeadAccount.ACCOUNT_TYPE_FACEBOOK:
                checks_wrong_password = self.checks_wrong_password_facebook
                checks_sec_checkpoint = self.checks_sec_checkpoint_facebook
            if lead_account.account_type == LeadAccount.ACCOUNT_TYPE_AMAZON:
                checks_wrong_password = self.checks_wrong_password_amazon
                checks_sec_checkpoint = self.checks_sec_checkpoint_amazon

            if checks_wrong_password >= self.WRONG_PASSWORD_CHECKS_MIN:
                note.append('{type} account has wrong PW ($0.00)'.format(
                    type=lead_account.get_account_type_display(),
                ))
                continue
            if checks_sec_checkpoint >= self.SEC_CHECKPOINT_CHECKS_MIN:
                note.append('{type} account has security checkpoint issue ($0.00)'.format(
                    type=lead_account.get_account_type_display(),
                ))
                continue

            if lead_account.account_type == LeadAccount.ACCOUNT_TYPE_GOOGLE:
                if lead_account.created > self.NEW_GOOGLE_MAX_PAYMENT_DATE:
                    month_payment = self.NEW_MAX_PAYMENT
                else:
                    month_payment = self.MAX_PAYMENT
            if lead_account.account_type == LeadAccount.ACCOUNT_TYPE_FACEBOOK:
                if lead_account.created > self.NEW_FACEBOOK_MAX_PAYMENT_DATE:
                    month_payment = self.NEW_MAX_PAYMENT
                else:
                    month_payment = self.MAX_PAYMENT
            if lead_account.account_type == LeadAccount.ACCOUNT_TYPE_AMAZON:
                month_payment = self.AMAZON_MAX_PAYMENT

            day_payment = round(month_payment / days_in_month, 4)
            note.append('{type} account created on {date} (${result})'.format(
                type=lead_account.get_account_type_display(),
                date=lead_account.created.strftime(settings.HUMAN_DATE_FORMAT),
                result=day_payment,
            ))
            result += day_payment

        note.append('Total: ${result}'.format(
            result=result,
        ))
        return result, '\n'.join(note)
