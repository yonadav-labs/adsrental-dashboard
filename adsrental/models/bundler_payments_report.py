import re

from django.db import models

from adsrental.models.lead_account import LeadAccount


class BundlerPaymentsReport(models.Model):
    '''
    Stores generated PDF and HTML report.
    '''
    date = models.DateField(db_index=True)
    pdf = models.FileField(upload_to='bundler_payments_reports')
    html = models.TextField()
    paid = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)

    def rollback(self):
        if self.cancelled:
            return False

        regexp = r'<td>([^<]+@[^<]+)</td>'
        emails = re.findall(regexp, self.html)
        lead_accounts = LeadAccount.objects.filter(username__in=emails, active=True, bundler_paid=True, bundler_paid_date=self.date)
        for lead_account in lead_accounts:
            lead_account.bundler_paid = False
            lead_account.save()
        lead_accounts = LeadAccount.objects.filter(username__in=emails, active=True, charge_back_billed=True)
        for lead_account in lead_accounts:
            lead_account.charge_back_billed = False
            lead_account.save()

        self.cancelled = True
        self.save()
