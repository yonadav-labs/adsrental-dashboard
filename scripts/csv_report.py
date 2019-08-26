# scp adsrental:/mnt/volume-nyc3-01/app_log/report.csv report.csv

import csv
from adsrental.models.lead_account import LeadAccount


las = LeadAccount.objects.filter(in_progress_date__gte=datetime.date(2018, 8, 26)).select_related('lead', 'lead__raspberry_pi', 'lead__bundler')


def format_date(x): return x.strftime('%Y-%m-%d') if x else 'n/a'


with open('/app/app_log/report.csv', 'w', newline='') as csvfile:
    fieldnames = [
        'Lead Account ID',
        'Lead Name',
        'RPID',
        'Account Type',
        'Status',
        'Bundler',
        'First seen',
        'Last Seen',
        'Qualified',
        'In progress',
        'Ban Reason',
        'Days Online',
        'Chargeback',
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for la in las:
        writer.writerow({
            'Lead Account ID': la.id,
            'Lead Name': la.lead.name(),
            'RPID': la.lead.raspberry_pi.rpid if la.lead.raspberry_pi else 'n/a',
            'Account Type': la.get_account_type_display(),
            'Status': la.get_status_display(),
            'Bundler': la.lead.bundler.name,
            'First seen': format_date(la.lead.raspberry_pi.first_seen) if la.lead.raspberry_pi else 'n/a',
            'Last Seen': format_date(la.lead.raspberry_pi.last_seen) if la.lead.raspberry_pi else 'n/a',
            'Qualified': format_date(la.qualified_date),
            'In progress': format_date(la.in_progress_date),
            'Ban Reason': la.ban_reason or 'n/a',
            'Days Online': la.get_active_days(),
            'Chargeback': la.charge_back,
        })
