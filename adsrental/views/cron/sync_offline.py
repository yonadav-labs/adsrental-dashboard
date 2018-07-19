import datetime

from django.views import View
from django.http import JsonResponse
from django.utils import timezone

from adsrental.models.lead import Lead
from adsrental.models.lead_account import LeadAccount
from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.utils import CustomerIOClient


class SyncOfflineView(View):
    '''
    Check :model:`adsrental.RaspberryPi` state and close sessions if device is offline. Send *offline* Cutomer.io event.
    Run by cron every 10 minutes.

    Parameters:

    * test - if 'true' does not close sessions and generate events, just provides output.
    '''

    def get(self, request):
        reported_offline_leads = []
        reported_checkpoint = []
        now = timezone.localtime(timezone.now())
        test = request.GET.get('test')
        customerio_client = CustomerIOClient()
        for lead in Lead.objects.filter(
                raspberry_pi__last_seen__lt=now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl + 60),
                pi_delivered=True,
                raspberry_pi__first_seen__isnull=False,
                status__in=Lead.STATUSES_ACTIVE,
        ).exclude(
            raspberry_pi__last_offline_reported__gte=now - datetime.timedelta(hours=RaspberryPi.last_offline_reported_hours_ttl),
        ).select_related('raspberry_pi'):
            offline_hours_ago = 1
            if lead.raspberry_pi.last_seen:
                offline_hours_ago = int((now - lead.raspberry_pi.last_seen).total_seconds() / 60 / 60)
            reported_offline_leads.append(lead.email)
            if test:
                continue

            customerio_client.send_lead_event(lead, CustomerIOClient.EVENT_OFFLINE, hours=offline_hours_ago)
            lead.raspberry_pi.report_offline()

        for lead_account in LeadAccount.objects.filter(
                security_checkpoint_date__isnull=False,
                status__in=LeadAccount.STATUSES_ACTIVE,
        ).exclude(
            last_security_checkpoint_reported__gte=now - datetime.timedelta(hours=LeadAccount.LAST_SECURITY_CHECKPOINT_REPORTED_HOURS_TTL),
        ).select_related('lead', 'lead__raspberry_pi'):
            reported_checkpoint.append(str(lead_account))
            if test:
                continue
            customerio_client.send_lead_event(lead_account.lead, CustomerIOClient.EVENT_SECURITY_CHECKPOINT, account_type=lead_account.account_type)
            lead_account.last_security_checkpoint_reported = now
            lead_account.save()

        return JsonResponse({
            'test': test,
            'result': True,
            'reported_offline_leads': reported_offline_leads,
            'reported_checkpoint': reported_checkpoint,
        })
