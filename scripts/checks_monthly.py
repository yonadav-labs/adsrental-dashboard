#!/usr/bin/env python
import datetime
from unittest import mock

LeadHistoryMonth = mock.MagicMock()

rpids = ''''''

for line in rpids.split('\n'):
    rpid, check_number = line.split()
    print(rpid)
    lhm = LeadHistoryMonth.objects.get(lead__raspberry_pi__rpid=rpid, date=datetime.date(2018, 10, 1))
    lhm.check_number = int(check_number)
    lhm.save()
