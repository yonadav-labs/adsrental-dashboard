#!/bin/python

# aws ec2 describe-instances --max-items 1000 > ~/instances.json
# aws ec2 describe-instances --max-items 1000 --starting-token eyJOZXh0VG9rZW4iOiBudWxsLCAiYm90b190cnVuY2F0ZV9hbW91bnQiOiAxMDAwfQ== > ~/instances2.json
# mysql -u root -h 0.0.0.0 -P 13306 adsrental -e "select raspberry_pi_id from lead where status!='Banned' and raspberry_pi_id is not null;" > ~/rpis.txt
# python ./scripts/cleanup.py ~/rpis.txt ~/instances.json | xargs -I % bash -c '%'
# python ./scripts/cleanup.py ~/rpis.txt ~/instances2.json | xargs -I % bash -c '%'


import sys
import json

f = open(sys.argv[1])
aws_json = json.loads(open(sys.argv[2]).read())
rpis = [i.rstrip('\n') for i in f.readlines()]
# print aws_json.keys()


for i in aws_json['Reservations']:
    for j in i['Instances']:
        is_used = False
        name = ''
        if 'Tags' not in j:
            continue
        for tagpair in j['Tags']:
            if tagpair.get('Key') != 'Name':
                continue
            name = tagpair.get('Value')
            value = tagpair.get('Value')
        if not name.startswith('RP'):
            continue
        if name in rpis:
            is_used = True
        # print j['InstanceId'], j['Tags'], is_used
        if not is_used:
            # print j['Tags']
            # print value
            print 'aws ec2 terminate-instances --instance-ids', j['InstanceId']
        # print j['Tags']
