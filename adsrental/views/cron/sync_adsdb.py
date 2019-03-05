from django.conf import settings
from django.http import JsonResponse, HttpRequest

from adsrental.models import LeadAccount, User
from adsrental.utils import AdsdbClient
from adsrental.views.cron.base import CronView


class SyncAdsDBView(CronView):
    def get(self, request: HttpRequest) -> JsonResponse:
        messages = []
        safe = request.GET.get('safe', '') == 'true'
        user = User.objects.get(email=settings.ADSDBSYNC_USER_EMAIL)
        known_ban_reasons = dict(LeadAccount.BAN_REASON_CHOICES).keys()
        lead_accounts = LeadAccount.objects.filter(adsdb_account_id__isnull=False).exclude(status=LeadAccount.STATUS_BANNED)

        if safe:
            lead_accounts.get_adsdb_data_safe(filters=AdsdbClient.BANNED_FILTERS, archive=True)
        else:
            lead_accounts.get_adsdb_data(archive=True)

        for lead_account in lead_accounts:
            if not lead_account.adsdb_account:
                continue

            adsdb_account = lead_account.adsdb_account
            if adsdb_account['account_status'] != 'Dead':
                continue

            ban_reason = LeadAccount.BAN_REASON_FACEBOOK_POLICY
            if lead_account.account_type == LeadAccount.ACCOUNT_TYPE_GOOGLE:
                ban_reason = LeadAccount.BAN_REASON_GOOGLE_POLICY
            if adsdb_account['ban_message'] in known_ban_reasons:
                ban_reason = adsdb_account['ban_message']

            messages.append(f'{lead_account.account_type} account {lead_account.username} banned for {ban_reason}')

            if self.is_execute():
                lead_account.ban(edited_by=user, reason=ban_reason)

        return self.render({
            'messages': messages,
            'total_banned': len(messages) - 1,
        })
