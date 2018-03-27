# pylint: skip-file

import requests
from django.conf import settings
from adsrental.models import *


def process_account(account):
    lead_account = LeadAccount.objects.filter(username=account['google_username'], password='').first()
    if lead_account and account['google_password']:
        lead_account.password = account['google_password']
        lead_account.save()
        print(lead_account.username, account['google_username'], account['google_password'])


auth = requests.auth.HTTPBasicAuth(settings.ADSDB_USERNAME, settings.ADSDB_PASSWORD)
for page in range(1, 100):
    print('Getting Page %d' % page)
    data = requests.post('https://www.adsdb.io/api/v1/accounts/get', auth=auth, json={'limit': 100, 'page': page}).json()
    if not data.get('success') or not data.get('data'):
        break
    for account in data['data']:
        process_account(account)
