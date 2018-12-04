import requests
from django.conf import settings
from django.views import View
from django.http import JsonResponse

from adsrental.models import LeadAccount, User


class SyncAdsDBView(View):
    def get(self, request):
        messages = []
        accounts = []
        auth = requests.auth.HTTPBasicAuth(settings.ADSDB_USERNAME, settings.ADSDB_PASSWORD)
        for page in range(1, 1000):
            data = requests.post(
                'https://www.adsdb.io/api/v1/accounts/get',
                auth=auth,
                json={
                    'limit': 200,
                    'page': page,
                },
            ).json()
            if not data.get('success') or not data.get('data'):
                break
            for account in data['data']:
                if account['account_status'] != 'Dead':
                    continue
                accounts.append(account)

        messages.append(f'Total accounts {len(accounts)}')
        user = User.objects.get(email='volshebnyi@gmail.com')
        for account in accounts:
            if account['account_status'] != 'Dead':
                continue
            if account.get('fb_username'):
                la = LeadAccount.objects.filter(username=account.get('fb_username'), account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK).first()
                if not la:
                    continue
                if la.status != LeadAccount.STATUS_BANNED:
                    messages.append(f'{la.account_type} account {la.username} banned from {la.status}')
                    la.ban(edited_by=user, reason=LeadAccount.BAN_REASON_FACEBOOK_POLICY)
                    continue
            if account.get('google_username'):
                la = LeadAccount.objects.filter(username=account.get('google_username'), account_type=LeadAccount.ACCOUNT_TYPE_GOOGLE).first()
                if not la:
                    continue
                if la.status != LeadAccount.STATUS_BANNED:
                    messages.append(f'{la.account_type} account {la.username} banned from {la.status}')
                    la.ban(edited_by=user, reason=LeadAccount.BAN_REASON_GOOGLE_POLICY)
                    continue

        return JsonResponse({
            'messages': messages,
            'total_banned': len(messages) - 1,
        })
