'LeadHistory class'
import datetime
from dateutil.relativedelta import relativedelta

from django.db import models
from adsrental.models.lead import Lead


class LeadHistory(models.Model):
    '''
    Aggregated daily stats for :model:`adsrental.Lead`.
    Used to calculate payments to leads.
    '''
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

        if self.lead.wrong_password_date:
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
        return self.checks_online > self.checks_offline

    def is_active(self):
        'Check password was not reported as wrong and device was online'
        return not self.is_wrong_password() and self.is_online()

    def is_wrong_password(self):
        'Check if password for this dayn was reported wrong at lead once.'
        return self.checks_wrong_password

    @classmethod
    def get_queryset_for_month(cls, year, month, lead_ids=None):
        'Get all entries for given year and month'
        date__gte = datetime.date(year, month, 1)
        date__lt = datetime.date(year, month, 1) + relativedelta(months=1)
        result = cls.objects.filter(date__gte=date__gte, date__lt=date__lt)
        if lead_ids:
            result = result.filter(lead_id__in=lead_ids)
        return result
