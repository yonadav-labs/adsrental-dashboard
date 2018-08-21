#!/usr/bin/env python
import os
import argparse
from pathlib import Path
import base64
import pymysql

import boto3
from Crypto.Cipher import DES3


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
password={password}
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
parser.add_argument('--id', help='EC2Instance Local ID')
parser.add_argument('-p', '--password', help='Password', default='')
args = parser.parse_args()
instance_id = None

if args.id:
    conn = pymysql.connect(host='localhost', port=23306, user='root', db='adsrental')
    cursor = conn.cursor()
    cursor.execute("SELECT rpid, password, instance_id FROM adsrental_ec2instance where id='{}'".format(args.id))
    for row in cursor:
        args.rpid = row[0]
        args.password = row[1]
        instance_id = row[2]

if not args.password:
    conn = pymysql.connect(host='localhost', port=23306, user='root', db='adsrental')
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM adsrental_ec2instance where rpid='{}'".format(args.rpid))
    for row in cursor:
        args.password = row[0]

secret = base64.b64decode('tCViJQOwkdqG88Ww9WpsVwc7CXBiwo89+5c0Y1awrgo=')
password = args.password.encode('ascii')
while len(password) < 16:
    password = password + b'\x00'

password_enc = base64.b64encode(DES3.new(secret[:24], DES3.MODE_CBC, secret[24:]).encrypt(password)).decode('ascii')

#  password=AlS+TjAugTD6El8ST/5Aeg==
# print(password_enc)
# exit()

rpid = None
if args.rpid:
    if args.rpid.isdigit():
        rpid = 'RP%08d' % int(args.rpid)
    else:
        rpid = args.rpid

boto_client = boto3.Session(
    aws_access_key_id='AKIAJ3IUVXDRV2ZS2QLQ',
    aws_secret_access_key='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',
).resource('ec2', region_name='us-west-2')

if instance_id:
    instances = boto_client.instances.filter(
        InstanceIds=[
            instance_id,
        ],
    )
elif args.email:
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
    print(i, i.state['Name'])
    if i.state['Name'] == 'running':
        instance = i
        break

print('Connecting to instance', instance.id, instance.tags, instance.public_dns_name, instance.state['Name'])

hostname = instance.public_dns_name

fname = '{home}/.remmina/{rpid}.remmina'.format(home=str(Path.home()), rpid=rpid)
with open(fname, 'w') as f:
    f.write(remmina_template.format(
        hostname=hostname,
        rpid=rpid,
        password=password_enc,
    ))
    f.flush()

command = 'remmina -c {}'.format(fname)
print(command)
os.system(command)
