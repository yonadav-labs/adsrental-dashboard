

from multiprocessing.pool import ThreadPool
import datetime
import logging
import argparse

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

from adsrental.models.lead_account import LeadAccount
from adsrental.models.lead_account_issue import LeadAccountIssue


class Command(BaseCommand):
    help = 'Fix not created issues'

    def handle(self, *args: str, **options: str) -> None:
        results = {
            'wrong_pw': [],
            'sec_checkpoint': [],
        }
        for la in LeadAccount.objects.filter(wrong_password_date__isnull=False):
            lai = LeadAccountIssue.objects.filter(lead_account=la, issue_type=LeadAccountIssue.ISSUE_TYPE_WRONG_PASSWORD).first()
            if not lai:
                results['wrong_pw'].append(f'{la}')
                LeadAccountIssue(
                    lead_account=la,
                    issue_type=LeadAccountIssue.ISSUE_TYPE_WRONG_PASSWORD,
                    created=la.wrong_password_date,
                ).save()

        for la in LeadAccount.objects.filter(security_checkpoint_date__isnull=False):
            lai = LeadAccountIssue.objects.filter(lead_account=la, issue_type=LeadAccountIssue.ISSUE_TYPE_SECURITY_CHECKPOINT).first()
            if not lai:
                results['sec_checkpoint'].append(f'{la}')
                LeadAccountIssue(
                    lead_account=la,
                    issue_type=LeadAccountIssue.ISSUE_TYPE_SECURITY_CHECKPOINT,
                    created=la.security_checkpoint_date,
                ).save()
