import datetime
import json

from dateutil import parser
import pytz
import requests
from django.conf import settings
from django.views import View
from django.http import JsonResponse, HttpRequest
from django.utils import timezone

from adsrental.models import LeadAccount, User


class SyncAdsDBView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        messages = []
        accounts = []
        not_found_count = 0
        now = timezone.localtime(timezone.now())
        auth = requests.auth.HTTPBasicAuth(settings.ADSDB_USERNAME, settings.ADSDB_PASSWORD)
        for page in range(1, 1000):
            try:
                data = requests.post(
                    'https://www.adsdb.io/api/v1/accounts/get',
                    auth=auth,
                    json={
                        'limit': 200,
                        'page': page,
                        'filters': {
                            'rules': [{'field': 'accounts.account_status', 'data': 3}]
                        }
                    },
                ).json()
            except (requests.RequestException, json.JSONDecodeError):
                continue
            if not data.get('success') or not data.get('data'):
                break
            for account in data['data']:
                if account['account_status'] != 'Dead':
                    continue
                try:
                    banned_date = parser.parse(account.get('dead_date')).astimezone(pytz.timezone(settings.TIME_ZONE))
                except ValueError:
                    continue

                if now - banned_date >= datetime.timedelta(days=4):
                    continue

                accounts.append(account)

        messages.append(f'Total accounts {len(accounts)}')
        user = User.objects.get(email=settings.ADSDBSYNC_USER_EMAIL)
        for account in accounts:
            if account['account_status'] != 'Dead':
                continue
            la = LeadAccount.objects.filter(adsdb_account_id=account.get('id')).first()
            if not la:
                not_found_count += 1
                continue
            if la.status == LeadAccount.STATUS_BANNED:
                continue

            messages.append(f'{la.account_type} account {la.username} banned from {la.status}')
            ban_reason = LeadAccount.BAN_REASON_QUIT
            if account['ban_message'] in dict(LeadAccount.BAN_REASON_CHOICES).keys():
                ban_reason = account['ban_message']
            la.ban(edited_by=user, reason=ban_reason)

        return JsonResponse({
            'messages': messages,
            'total_banned': len(messages) - 1,
            'not_found': not_found_count,
        })
