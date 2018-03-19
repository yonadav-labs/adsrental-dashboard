#!/usr/bin/env python
import os
import argparse
from pathlib import Path

import boto3


remmina_template = '''[remmina]
disableclipboard=0
ssh_auth=0
clientname=
quality=0
ssh_charset=
ssh_privatekey=
console=0
resolution=
group=
password=FFyY5EresaY6/GxvPzqkLg==
name={rpid}
ssh_loopback=0
shareprinter=0
ssh_username=
ssh_server=
security=
protocol=RDP
execpath=
sound=off
exec=
ssh_enabled=0
username=Administrator
sharefolder=
domain=
server={hostname}:23255
colordepth=32
window_maximize=1
window_height=967
viewmode=1
window_width=1812
scale=1
sharesmartcard=0
'''

parser = argparse.ArgumentParser(description='Connect to RDP by RPID or email.')
parser.add_argument('--rpid', help='RPID for Raspberry Pi')
parser.add_argument('--email', help='Lead email')
args = parser.parse_args()

rpid = None
if args.rpid:
    if args.rpid.isdigit():
        rpid = 'RP%08d' % int(args.rpid)
    else:
        rpid = args.rpid

if not args.rpid and not args.email:
    rpid = input('Enter RPID: ')

boto_client = boto3.Session(
    aws_access_key_id='AKIAJ3IUVXDRV2ZS2QLQ',
    aws_secret_access_key='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',
).resource('ec2', region_name='us-west-2')

if args.email:
    instances = boto_client.instances.filter(
        Filters=[
            {
                'Name': 'tag:Email',
                'Values': [args.email],
            },
        ],
    )
else:
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
    if i.state['Name'] == 'running':
        instance = i

print('Connecting to instance', instance.id, instance.tags, instance.public_dns_name, instance.state['Name'])

hostname = instance.public_dns_name

fname = '{home}/.remmina/{rpid}.remmina'.format(home=str(Path.home()), rpid=rpid)
with open(fname, 'w') as f:
    f.write(remmina_template.format(
        hostname=hostname,
        rpid=rpid,
    ))
    f.flush()

command = 'remmina -c {}'.format(fname)
print(command)
os.system(command)
