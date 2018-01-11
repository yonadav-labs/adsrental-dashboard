#!/usr/bin/env python
import os
import sys
import boto3

try:
    rpid = sys.argv[1]
except:
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

command = 'rdpy-rdpclient.py -u Administrator -p Dk.YDq8pXQS-R5ZAn84Lgma9rFvGlfvL {}:23255'.format(hostname)
print command
os.system(command)
