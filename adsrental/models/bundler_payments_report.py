import re
import json
import decimal

from django.db import models
from django.conf import settings
from django.core.mail import EmailMessage

from adsrental.models.lead_account import LeadAccount


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

    def get_usernames(self):
        regexp = r'<td>([^<]+@[^<]+)</td>'
        emails = re.findall(regexp, self.html)

        regexp = r'<td>(\d{8,40})</td>'
        phones = re.findall(regexp, self.html)
        usernames = phones + emails
        return usernames

    def get_lead_accounts(self):
        usernames = self.get_usernames()
        lead_accounts = LeadAccount.objects.filter(username__in=usernames, active=True, bundler_paid=True, bundler_paid_date=self.date)
        return lead_accounts

    def get_html_for_bundler(self, bundler):
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

    def mark(self):
        result = {
            'facebook_entries_ids': 0,
            'chargeback_facebook_entries_ids': 0,
            'google_entries_ids': 0,
            'chargeback_google_entries_ids': 0,
        }
        for data in json.loads(self.data):
            facebook_entries_ids = [i['id'] for i in data['facebook_entries'] if decimal.Decimal(i['payment']) >= 0]
            chargeback_facebook_entries_ids = [i['id'] for i in data['facebook_entries'] if decimal.Decimal(i['payment']) < 0]
            google_entries_ids = [i['id'] for i in data['google_entries'] if decimal.Decimal(i['payment']) >= 0]
            chargeback_google_entries_ids = [i['id'] for i in data['google_entries'] if decimal.Decimal(i['payment']) < 0]
            amazon_entries_ids = [i['id'] for i in data['amazon_entries'] if decimal.Decimal(i['payment']) >= 0]
            chargeback_amazon_entries_ids = [i['id'] for i in data['amazon_entries'] if decimal.Decimal(i['payment']) < 0]

            result['facebook_entries_ids'] += len(facebook_entries_ids)
            result['chargeback_facebook_entries_ids'] += len(chargeback_facebook_entries_ids)
            result['google_entries_ids'] += len(google_entries_ids)
            result['chargeback_google_entries_ids'] += len(chargeback_google_entries_ids)
            result['amazon_entries_ids'] += len(amazon_entries_ids)
            result['chargeback_amazon_entries_ids'] += len(chargeback_amazon_entries_ids)

            LeadAccount.objects.filter(id__in=facebook_entries_ids).update(
                bundler_paid_date=self.date,
                bundler_paid=True,
            )
            LeadAccount.objects.filter(id__in=chargeback_facebook_entries_ids).update(
                charge_back_billed=True,
            )
            LeadAccount.objects.filter(id__in=google_entries_ids).update(
                bundler_paid_date=self.date,
                bundler_paid=True,
            )
            LeadAccount.objects.filter(id__in=chargeback_google_entries_ids).update(
                charge_back_billed=True,
            )
            LeadAccount.objects.filter(id__in=amazon_entries_ids).update(
                bundler_paid_date=self.date,
                bundler_paid=True,
            )
            LeadAccount.objects.filter(id__in=chargeback_amazon_entries_ids).update(
                charge_back_billed=True,
            )

        self.cancelled = False
        self.save()

        return result

    def unmark(self):
        result = {
            'facebook_entries_ids': 0,
            'chargeback_facebook_entries_ids': 0,
            'google_entries_ids': 0,
            'chargeback_google_entries_ids': 0,
        }
        for data in json.loads(self.data):
            facebook_entries_ids = [i['id'] for i in data['facebook_entries'] if decimal.Decimal(i['payment']) >= 0]
            chargeback_facebook_entries_ids = [i['id'] for i in data['facebook_entries'] if decimal.Decimal(i['payment']) < 0]
            google_entries_ids = [i['id'] for i in data['google_entries'] if decimal.Decimal(i['payment']) >= 0]
            chargeback_google_entries_ids = [i['id'] for i in data['google_entries'] if decimal.Decimal(i['payment']) < 0]
            amazon_entries_ids = [i['id'] for i in data['amazon_entries'] if decimal.Decimal(i['payment']) >= 0]
            chargeback_amazon_entries_ids = [i['id'] for i in data['amazon_entries'] if decimal.Decimal(i['payment']) < 0]

            result['facebook_entries_ids'] += len(facebook_entries_ids)
            result['chargeback_facebook_entries_ids'] += len(chargeback_facebook_entries_ids)
            result['google_entries_ids'] += len(google_entries_ids)
            result['chargeback_google_entries_ids'] += len(chargeback_google_entries_ids)
            result['amazon_entries_ids'] += len(amazon_entries_ids)
            result['chargeback_amazon_entries_ids'] += len(chargeback_amazon_entries_ids)

            LeadAccount.objects.filter(id__in=facebook_entries_ids).update(
                bundler_paid_date=None,
                bundler_paid=False,
            )
            LeadAccount.objects.filter(id__in=chargeback_facebook_entries_ids).update(
                charge_back_billed=False,
            )
            LeadAccount.objects.filter(id__in=google_entries_ids).update(
                bundler_paid_date=None,
                bundler_paid=False,
            )
            LeadAccount.objects.filter(id__in=chargeback_google_entries_ids).update(
                charge_back_billed=False,
            )
            LeadAccount.objects.filter(id__in=amazon_entries_ids).update(
                bundler_paid_date=None,
                bundler_paid=False,
            )
            LeadAccount.objects.filter(id__in=chargeback_amazon_entries_ids).update(
                charge_back_billed=False,
            )
        self.cancelled = True
        self.save()
        return result

    def send_by_email(self):
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
