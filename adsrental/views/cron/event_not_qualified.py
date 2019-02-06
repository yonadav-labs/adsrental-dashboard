import datetime

from django.utils import timezone
from django.views import View
from django.conf import settings
from django.http import JsonResponse, HttpRequest

from adsrental.models.lead_account import LeadAccount
from adsrental.utils import CustomerIOClient


class EventNotQualifiedView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        if not request.META.get('HTTP_SECRET', '') == settings.CRON_SECRET:
            return JsonResponse({'error': 'no secret'})

        time_deltas = [
            datetime.timedelta(days=1),
            datetime.timedelta(days=3),
            datetime.timedelta(days=7),
        ]
        max_timedelta = datetime.timedelta(days=8)
        now = timezone.localtime(timezone.now())
        lead_accounts = LeadAccount.objects.filter(status=LeadAccount.STATUS_AVAILABLE, created__gt=now - max_timedelta).prefetch_related('lead')
        sent = []
        for lead_account in lead_accounts:
            delta_not_qualified = now - lead_account.created
            last_not_qualified_reported = lead_account.last_not_qualified_reported or now - max_timedelta
            for time_delta in time_deltas:
                if delta_not_qualified > time_delta and lead_account.created + time_delta > last_not_qualified_reported:
                    lead_account.last_not_qualified_reported = now
                    lead_account.save()
                    CustomerIOClient().send_lead_event(lead_account.lead, CustomerIOClient.EVENT_NOT_QUALIFIED, days=delta_not_qualified.days)
                    sent.append({'email': lead_account.lead.email, 'days_not_qualified': delta_not_qualified.days})
                    break
        return JsonResponse({'result': True, 'count': len(sent), 'sent': sent})
