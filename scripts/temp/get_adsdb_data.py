# pylint: skip-file

import json

import requests
from django.conf import settings
from adsrental.models.lead_account import LeadAccount

# ids = tuple(map(lambda x: x[0], LeadAccount.objects.filter(adsdb_account_id__isnull=False, status=LeadAccount.STATUS_IN_PROGRESS).values_list('adsdb_account_id')))
# ids_filter = ','.join(ids)

accounts = []
auth = requests.auth.HTTPBasicAuth(settings.ADSDB_USERNAME, settings.ADSDB_PASSWORD)
for page in range(1, 1000):
    print('Getting Page %d' % page)
    data = requests.post(
        'https://www.adsdb.io/api/v1/accounts/get',
        auth=auth,
        json={
            'limit': 200,
            # 'ids': ids_filter,
            'page': page,
            'filters': {'rules': [{'field': 'accounts.account_status', 'data': 3}]}
        },
    ).json()
    accounts += data['data']
    if not data.get('count') <= len(accounts):
        break
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
        ban_reason = LeadAccount.BAN_REASON_QUIT
        if account['ban_message'] in dict(LeadAccount.BAN_REASON_CHOICES).keys():
            ban_reason = account['ban_message']
        la.ban(edited_by=user, reason=ban_reason)
        la.save()
