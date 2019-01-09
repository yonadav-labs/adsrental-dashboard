#!/usr/bin/env python
import datetime

from adsrental.models.lead_history_month import LeadHistoryMonth

rpids = ''''''

for line in rpids.split('\n'):
    rpid, check_number = line.split()
    try:
        lhm = LeadHistoryMonth.objects.get(lead__raspberry_pi__rpid=rpid, date=datetime.date(2018, 12, 1))
    except LeadHistoryMonth.DoesNotExist:
        print(rpid, 'NOT FOUND!')
        continue
    if not lhm.check_number:
        print(rpid, 'set to', check_number)
        lhm.check_number = int(check_number)
        lhm.save()
