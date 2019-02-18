from __future__ import annotations

import json
import typing

from django.db import models
from django.conf import settings
from django.core.mail import EmailMessage

from adsrental.models.lead_account import LeadAccount

if typing.TYPE_CHECKING:
    from adsrental.models.bundler import Bundler


class BundlerPaymentsReport(models.Model):
    '''
    Stores generated PDF and HTML report.
    '''
    date = models.DateField(db_index=True)
    pdf = models.FileField(upload_to='bundler_payments_reports')
    html = models.TextField()
    paid = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    data = models.TextField(default='')
    cancelled = models.BooleanField(default=False)

    def __str__(self):
        return f'Bundler payments report for {self.date}'

    def get_lead_accounts(self) -> models.query.QuerySet:
        result = []
        if not self.data:
            return result
        data = json.loads(self.data)
        keys = ['facebook_entries', 'google_entries', 'amazon_entries']
        for entry in data:
            for key in keys:
                for lead_account_entry in entry[key]:
                    result.append(LeadAccount.objects.get(id=lead_account_entry['id']))

        return result

    def get_html_for_bundler(self, bundler: Bundler) -> str:
        html = self.html
        html_parts = html.split('<h3>')
        result = []
        result.append(html[0])
        utm_source_string = '(UTM source {})'.format(bundler.utm_source)
        for part in html_parts[1:-1]:
            part_header, part_no_header = part.split('</h3>', 1)
            if utm_source_string in part_header:
                result.append('<h3>(UTM source {})</h3>{}'.format(bundler.utm_source, part_no_header))

        # result.append('<h3>' + html_parts[-1])
        return ''.join(result)

    def send_by_email(self) -> None:
        email = EmailMessage(
            'Payments report for {}'.format(self.date.strftime(settings.HUMAN_DATE_FORMAT)),
            'Payments report for {}'.format(self.date.strftime(settings.HUMAN_DATE_FORMAT)),
            'Adsrental Reporting <reporting@adsrental.com>',
            settings.REPORT_RECIPIENTS,
        )
        email.attach('report_{}.pdf'.format(self.date), content=self.pdf.read(), mimetype='text/pdf')
        email.send()
        self.email_sent = True
        self.save()
