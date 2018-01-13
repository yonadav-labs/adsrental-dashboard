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
            raspberry_pi__last_seen__lt=now - datetime.timedelta(hours=RaspberryPi.online_hours_ttl),
            raspberry_pi__last_offline_reported__lt=now - datetime.timedelta(hours=RaspberryPi.last_offline_reported_hours_ttl),
            pi_delivered=True,
            raspberry_pi__first_seen__isnull=False,
            status=Lead.STATUS_QUALIFIED,
        ).select_related('raspberry_pi'):
            offline_hours_ago = 1
            if lead.raspberry_pi.last_seen:
                offline_hours_ago = int((now - lead.raspberry_pi.last_seen).total_seconds() / 60 / 60)
            if not test:
                customerio_client.send_lead_event(lead, 'offline', hours=offline_hours_ago)
                reported_offline_leads.append(lead.email)
                lead.raspberry_pi.last_offline_reported = timezone.now()
                lead.raspberry_pi.save()

        return JsonResponse({
            'test': test,
            'result': True,
            'reported_offline_leads': reported_offline_leads,
        })
