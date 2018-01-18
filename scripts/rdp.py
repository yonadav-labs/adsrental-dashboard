#!/usr/bin/env python
import os
import argparse

import boto3


parser = argparse.ArgumentParser(description='Connect to RDP by RPID or email.')
parser.add_argument('rpid', help='RPID for Raspberry Pi')
# parser.add_argument('--email', help='Lead email')
args = parser.parse_args()

rpid = None
if args.rpid:
    if args.rpid.isdigit():
        rpid = 'RP%08d' % int(args.rpid)
    else:
        rpid = args.rpid

if not rpid:
    rpid = raw_input('Enter RPID: ')

boto_client = boto3.Session(
    aws_access_key_id='AKIAJ3IUVXDRV2ZS2QLQ',
    aws_secret_access_key='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',
).resource('ec2', region_name='us-west-2')


instances = boto_client.instances.filter(
    Filters=[
        {
            'Name': 'tag:Name',
            'Values': [rpid],
        },
    ],
)

if not instances:
    print('No instances')
    exit()

instance = None
for i in instances:
    instance = i
print 'instance', rpid, instance, instance.public_dns_name

hostname = instance.public_dns_name

command = 'rdpy-rdpclient.py -w {width} -l {height} -u Administrator -p Dk.YDq8pXQS-R5ZAn84Lgma9rFvGlfvL {hostname}:23255'.format(
    width=1024,
    height=800,
    hostname=hostname,
)
print command
os.system(command)
