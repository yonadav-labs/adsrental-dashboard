import os
import datetime

from django.core.management.base import BaseCommand
from django.conf import settings

from adsrental.models.lead import Lead
from adsrental.models.lead_history import LeadHistory
from adsrental.models.lead_history_month import LeadHistoryMonth


class Command(BaseCommand):
    help = 'Create record entries'

    def add_arguments(self, parser):
        parser.add_argument('--now', action='store_true')
        parser.add_argument('--force', action='store_true')
        parser.add_argument('--date')
        parser.add_argument('--aggregate', action='store_true')

    def handle(
        self,
        now,
        date,
        force,
        aggregate,
        **kwargs
    ):
        if now:
            leads = Lead.objects.filter(status=Lead.STATUS_QUALIFIED, raspberry_pi__isnull=False).select_related('raspberry_pi')
            for lead in leads:
                LeadHistory.upsert_for_lead(lead)
            return 'Done'
        if aggregate:
            leads = Lead.objects.filter(status=Lead.STATUS_QUALIFIED, raspberry_pi__isnull=False).select_related('raspberry_pi')
            d = datetime.datetime.strptime(date, '%Y-%m-%d').date() if date else datetime.date.today()
            d = d.replace(day=1)
            for lead in leads:
                LeadHistoryMonth.get_or_create(lead=lead, date=d).aggregate()
            return 'Done'
        if date:
            leads = Lead.objects.filter(status=Lead.STATUS_QUALIFIED, raspberry_pi__isnull=False).select_related('raspberry_pi')
            d = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            if force:
                LeadHistory.objects.filter(date=d).delete()
            for lead in leads:
                if not force:
                    lead_history = LeadHistory.objects.filter(lead=lead, date=d).first()
                    if lead_history:
                        continue

                log_filename = '{}.log'.format(d.strftime('%Y%m%d'))
                log_path = os.path.join(settings.RASPBERRY_PI_LOG_PATH, lead.raspberry_pi.rpid, log_filename)
                is_online = os.path.exists(log_path)
                LeadHistory(lead=lead, date=d, checks_online=24 if is_online else 0, checks_offline=24 if not is_online else 0).save()
                # print lead, is_online
            return 'Done'
