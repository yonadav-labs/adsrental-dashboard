# pylint: skip-file

import json

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

user = User.objects.get(email=settings.ADSDBSYNC_USER_EMAIL)


# assign IDS
# for account in accounts:
#     print(account['api_name'])
#     break
#     account_id = account.get('id')
#     la = LeadAccount.objects.filter(adsdb_account_id=str(account_id)).first()
#     if la:
#         continue

#     if account.get('google_username'):
#         la = LeadAccount.objects.filter(username=account.get('google_username'), account_type=LeadAccount.ACCOUNT_TYPE_GOOGLE).first()

#     if account.get('fb_username'):
#         la = LeadAccount.objects.filter(username=account.get('fb_username'), account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK).first()

#     if la:
#         print('Assigned id', account_id, la)
#         # la.adsdb_account_id = str(account_id)
#         # la.save()
#         continue

# ban dead
for account in accounts:
    if account['account_status'] != 'Dead':
        continue
    account_id = account.get('id')
    la = LeadAccount.objects.filter(adsdb_account_id=str(account_id)).first()
    if not la:
        # print('FB not found', account.get('fb_username'))
        continue
    if la.status != LeadAccount.STATUS_BANNED:
        print('Account will be banned', la.username, la.account_type, la.status)
        la.insert_note('Banned by sync script')
        la.ban(edited_by=user, reason=LeadAccount.BAN_REASON_QUIT)
        la.save()
