# pylint: skip-file

import requests
from django.conf import settings
from adsrental.models import *

accounts = []
auth = requests.auth.HTTPBasicAuth(settings.ADSDB_USERNAME, settings.ADSDB_PASSWORD)
for page in range(1, 1000):
    print('Getting Page %d' % page)
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
    accounts += data['data']
    print('Total', len(accounts))

user = User.objects.get(email='volshebnyi@gmail.com')
for account in accounts:
    if account['account_status'] == 'Dead':
        if account.get('fb_username'):
            la = LeadAccount.objects.filter(username=account.get('fb_username'), account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK).first()
            if not la:
                # print('FB not found', account.get('fb_username'))
                continue
            if la.status != LeadAccount.STATUS_BANNED:
                print('FB will be banned', la.username, la.status)
                la.ban(edited_by=user, reason=LeadAccount.BAN_REASON_FACEBOOK_POLICY)
                continue
        if account.get('google_username'):
            la = LeadAccount.objects.filter(username=account.get('google_username'), account_type=LeadAccount.ACCOUNT_TYPE_GOOGLE).first()
            if not la:
                # print('Google not found', account.get('google_username'))
                continue
            if la.status != LeadAccount.STATUS_BANNED:
                print('Google will be banned', la.username, la.status)
                la.ban(edited_by=user, reason=LeadAccount.BAN_REASON_GOOGLE_POLICY)
                continue
