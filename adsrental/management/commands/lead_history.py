from django.core.management.base import BaseCommand

from adsrental.models.lead import Lead
from adsrental.models.lead_history import LeadHistory


class Command(BaseCommand):
    help = 'Create record entries'

    def handle(
        self,
        **kwargs
    ):
        leads = Lead.objects.filter(status=Lead.STATUS_QUALIFIED, raspberry_pi__isnull=False)
        for lead in leads:
            LeadHistory.upsert_for_lead(lead)
