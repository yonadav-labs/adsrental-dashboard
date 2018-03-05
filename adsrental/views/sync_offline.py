from __future__ import unicode_literals

import datetime

from django.views import View
from django.http import JsonResponse
from django.utils import timezone

from adsrental.models.lead import Lead
from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.utils import CustomerIOClient


class SyncOfflineView(View):
    def get(self, request):
        reported_offline_leads = []
        now = timezone.now()
        test = request.GET.get('test')
        customerio_client = CustomerIOClient()
        for lead in Lead.objects.filter(
            raspberry_pi__last_seen__lt=now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl + 60),
            raspberry_pi__last_offline_reported__lt=now - datetime.timedelta(hours=RaspberryPi.last_offline_reported_hours_ttl),
            pi_delivered=True,
            raspberry_pi__first_seen__isnull=False,
            status__in=Lead.STATUSES_ACTIVE,
        ).select_related('raspberry_pi'):
            offline_hours_ago = 1
            if lead.raspberry_pi.last_seen:
                offline_hours_ago = int((now - lead.raspberry_pi.last_seen).total_seconds() / 60 / 60)
            reported_offline_leads.append(lead.email)
            if test:
                continue

            customerio_client.send_lead_event(lead, CustomerIOClient.EVENT_OFFLINE, hours=offline_hours_ago)
            lead.raspberry_pi.report_offline()

        return JsonResponse({
            'test': test,
            'result': True,
            'reported_offline_leads': reported_offline_leads,
        })
