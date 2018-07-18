'Helper classes'
import json
import time
import uuid
import secrets
import string
import random

import requests
import boto3
from botocore.exceptions import ClientError
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from django.apps import apps
import customerio
from shipstation.api import ShipStation, ShipStationOrder, ShipStationAddress, ShipStationItem, ShipStationWeight

from adsrental.models.customerio_event import CustomerIOEvent


class CustomerIOClient(object):
    '''Manages lead data ans send events for leads to customer.io'''
    EVENT_SHIPPED = 'shipped'
    EVENT_DELIVERED = 'delivered'
    EVENT_OFFLINE = 'offline'
    EVENT_APPROVED = 'lead_approved'
    EVENT_BANNED = 'banned'
    EVENT_AVAILABLE_BANNED = 'available_banned'
    EVENT_BANNED_HAS_ACCOUNTS = 'banned_has_accounts'
    EVENT_SECURITY_CHECKPOINT = 'security_checkpoint'

    def __init__(self):
        self.client = None
        if not settings.CUSTOMERIO_ENABLED:
            return
        self.client = customerio.CustomerIO(
            settings.CUSTOMERIO_SITE_ID, settings.CUSTOMERIO_API_KEY)

    def get_client(self):
        '''
        Get customer.io client

        Returns:
            customerio.CustomerIO instance.
        '''
        return self.client

    def send_lead(self, lead):
        '''
        Save lead info like email and phone to customer.io database.

        *lead* - :model:`adsrental.Lead` instance

        Returns customerio.CustomerIO instance.
        '''
        clean_phone = '+1' + (''.join([i for i in lead.phone if i.isdigit()]))
        if self.client:
            self.client.identify(
                id=lead.leadid,
                First_Name=lead.first_name,
                Last_Name=lead.last_name,
                Phone=clean_phone,
                Raspberry_Pi=lead.raspberry_pi.rpid if lead.raspberry_pi else '',
                tracking_code=lead.usps_tracking_code,
                Raspberry_Pi_Status='Online' if (lead.raspberry_pi and lead.raspberry_pi.online()) else 'Offline',
                Status=lead.status,
                email=lead.email,
                Activation_Link='https://adsrental.com/check.html?',
                Reactivate_Url='https://adsrental.com/reactivate.html?',
                created_at=lead.created.strftime('%s'),
                Company=lead.company,

            )

    def send_lead_event(self, lead, event, **kwargs):
        '''
        Create a new :model:`adsrental.Lead` event, like banned or approved.

        *lead* - :model:`adsrental.Lead` instance
        *event* - event name, should be one of listed.
        All other keyword arguments are passed to  CustomerIOEvent kwrags

        Returns customerio.CustomerIO instance.
        '''
        send = True
        if not self.client:
            send = False
        if not lead.customerio_enabled:
            send = False
        CustomerIOEvent(
            lead=lead,
            name=event,
            sent=send,
            kwargs=json.dumps(kwargs),
        ).save()
        if send:
            self.client.track(customer_id=lead.leadid, name=event, **kwargs)

    def is_enabled(self):
        'Check if client is initialized.'
        return self.client is not None


class ShipStationClient(object):
    'Handles order creation and check on shipstation.'
    def __init__(self):
        self.client = ShipStation(
            key=settings.SHIPSTATION_API_KEY, secret=settings.SHIPSTATION_API_SECRET)

    def get_client(self):
        'Get native shipstation client'
        return self.client

    def add_lead_order(self, lead, status=None):
        'Create order for given lead.'
        if not lead.shipstation_order_number:
            random_str = str(uuid.uuid4()).replace('-', '')[:10]
            lead.shipstation_order_number = '{}__{}'.format(lead.raspberry_pi.rpid, random_str)
            lead.save()

        order = ShipStationOrder(
            order_key=lead.shipstation_order_number, order_number=lead.shipstation_order_number)
        order.set_customer_details(
            username=lead.safe_name(),
            email=lead.email,
        )

        if status:
            order.set_status(status)

        shipping_address = ShipStationAddress(
            name=lead.safe_name(),
            # company=sf_lead.company,
            street1=lead.street,
            city=lead.city,
            postal_code=lead.postal_code,
            # country=sf_lead.country,
            country='US',
            state=lead.state or '',
            phone=lead.phone or lead.mobile_phone,
        )
        order.set_shipping_address(shipping_address)
        order.set_billing_address(shipping_address)

        item = ShipStationItem(
            name=lead.raspberry_pi.rpid,
            quantity=1,
            unit_price=0,
        )
        item.set_weight(ShipStationWeight(units='ounces', value=0))
        order.add_item(item)

        order.set_status('awaiting_shipment')

        self.client.add_order(order)
        self.submit_orders()
        return order

    def submit_orders(self):
        'Submit all created or changed orders.'
        for order in self.client.orders:
            self.post(
                endpoint='/orders/createorder',
                data=json.dumps(order.as_dict())
            )

    def post(self, endpoint='', data=None):
        'Rewrite original shipstaion.post method to catch exceptions.'
        url = '{}{}'.format(self.client.url, endpoint)
        headers = {'content-type': 'application/json'}
        response = requests.post(
            url,
            auth=(self.client.key, self.client.secret),
            data=data,
            headers=headers
        )
        if response.status_code not in [200, 201]:
            raise ValueError('Shipstation Error', response.status_code, response.text)

    @staticmethod
    def get_lead_order_data(lead):
        'Get order data for lead.'
        if not lead.shipstation_order_number:
            return None
        data = requests.get(
            'https://ssapi.shipstation.com/orders',
            params={'orderNumber': lead.shipstation_order_number},
            auth=requests.auth.HTTPBasicAuth(
                settings.SHIPSTATION_API_KEY, settings.SHIPSTATION_API_SECRET),
        ).json().get('orders')
        data = data[0] if data else None
        return data


class BotoResource(object):
    'Handles AWS boto operations.'
    def __init__(self):
        self.session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        self.resources = {}

    def get_resource(self, service='ec2'):
        'Get boto resource for given service. Chaches results.'
        if not self.resources.get(service):
            resource = self.session.resource(
                service, region_name=settings.AWS_REGION)
            self.resources[service] = resource

        return self.resources[service]

    def get_client(self, service):
        return self.session.client(service, region_name=settings.AWS_REGION)

    def get_by_essential_key(self, key):
        'Get first valid instnce for given RPID.'
        instances = self.get_resource('ec2').instances.filter(
            Filters=[
                {
                    'Name': 'tag:EssentialKey',
                    'Values': [key],
                },
            ],
        )
        instances_list = [i for i in instances]
        for instance in instances_list:
            return instance

    def get_first_rpid_instance(self, rpid):
        'Get first valid instnce for given RPID.'
        instances = self.get_resource('ec2').instances.filter(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': [rpid],
                },
            ],
        )
        instances_list = [i for i in instances]
        for instance in instances_list:
            instance_state = instance.state['Name']
            if self.get_instance_tag(instance, 'Duplicate') == 'true':
                continue

            if instance_state != 'running':
                continue

            return instance

        for instance in instances_list:
            if instance_state == 'terminated' or instance_state == 'shutting-down':
                continue

            if self.get_instance_tag(instance, 'Duplicate') == 'true':
                continue

            return instance

        for instance in instances_list:
            instance_state = instance.state['Name']
            if instance_state == 'terminated' or instance_state == 'shutting-down':
                continue
            return instance

        return False

    @staticmethod
    def get_instance_tag(instance, key):
        'Get instance tag value by key'
        if not instance.tags:
            return None

        for tagpair in instance.tags:
            if tagpair['Key'] == key:
                return tagpair['Value']

        return None

    def set_instance_tag(self, instance, key, value):
        'Set instance tag value by key'
        tags = instance.tags or []
        key_found = False
        for tagpair in tags:
            if tagpair['Key'] == key:
                key_found = True
                tagpair['Value'] = value
                break
        if not key_found:
            tags.append({'Key': key, 'Value': value})

        try:
            self.get_resource('ec2').create_tags(
                Resources=[instance.id], Tags=tags)
        except ClientError:
            pass

    def create_r53_entry(self, ec2_instance):
        ec2_resource = self.get_resource('ec2')
        route53_client = boto3.client('route53')
        hostname = ec2_instance.get_r53_hostname()
        elastic_ip = ec2_resource.allocate_address(Domain='vpc')
        ec2_resource.associate_address(
            InstanceId=ec2_instance.instance_id,
            AllocationId=elastic_ip["AllocationId"],
        )
        route53_client.change_resource_record_sets(
            HostedZoneId=settings.AWS_R53_ZONE_ID,
            ChangeBatch={
                'Comment': 'Add {} instance to Route53'.format(ec2_instance.rpid),
                'Changes': [
                    {
                        'Action': 'CREATE',
                        'ResourceRecordSet': {
                            'Name': hostname,
                            'Type': 'A',
                            'TTL': 60,
                            'ResourceRecords': [
                                {
                                    'Value': elastic_ip["PublicIp"],
                                },
                            ],
                        }
                    },
                ]
            },
        )

    def launch_instance(self, rpid, email):
        'Start otr create AWS EC2 instance for given RPID'
        instance = self.get_first_rpid_instance(rpid)
        if not instance:
            self.get_resource('ec2').create_instances(
                ImageId=settings.AWS_IMAGE_AMI,
                MinCount=1,
                MaxCount=1,
                KeyName='AI Farming Key',
                InstanceType='t2.medium',
                SecurityGroupIds=settings.AWS_SECURITY_GROUP_IDS,
                UserData=rpid,
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': rpid,
                            },
                            {
                                'Key': 'Email',
                                'Value': email or '',
                            },
                            {
                                'Key': 'Duplicate',
                                'Value': 'false',
                            },
                        ]
                    },
                ],
            )
            time.sleep(5)
            instance = self.get_first_rpid_instance(rpid)
            if not instance:
                raise ValueError('Boto did not create isntance. Try again.')

            # instance.password = generate_password(length=12)
            # instance.save()

        ec2_instance_model = apps.get_app_config('adsrental').get_model('EC2Instance')
        instance = ec2_instance_model.upsert_from_boto(instance)
        return instance

    @staticmethod
    def generate_key():
        return str(uuid.uuid4())

    def launch_essential_instance(self, ec2_instance):
        'Start or create AWS EC2 instance for given RPID'
        boto_instance = self.get_by_essential_key(ec2_instance.essential_key)
        if boto_instance:
            return ec2_instance

        self.get_resource('ec2').create_instances(
            ImageId=settings.AWS_IMAGE_AMI_ESSENTIAL,
            MinCount=1,
            MaxCount=1,
            KeyName='AI Farming Key',
            InstanceType=ec2_instance.instance_type,
            SecurityGroupIds=settings.AWS_SECURITY_GROUP_IDS,
            UserData='essential',
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Essential',
                            'Value': 'true',
                        },
                        {
                            'Key': 'EssentialKey',
                            'Value': ec2_instance.essential_key,
                        },
                        {
                            'Key': 'Duplicate',
                            'Value': 'false',
                        },
                    ]
                },
            ],
        )
        time.sleep(5)
        boto_instance = self.get_by_essential_key(ec2_instance.essential_key)
        if not boto_instance:
            raise ValueError('Boto did not create isntance. Try again.')

        ec2_instance.instance_id = boto_instance.id
        ec2_instance.save()

        ec2_instance.update_from_boto(boto_instance)
        return boto_instance


class PingCacheHelper(object):
    'Simplifies cache operations for updating timestamps'
    KEY_TEMPLATE = 'ping_{}'
    KEYS = 'ping_keys'
    TTL_SECONDS = 600
    CACHE_VERSION = '1.0.1'

    def __init__(self):
        self.cache = cache

    def get_key(self, rpid):
        'Get keys string for given rpid'
        return self.KEY_TEMPLATE.format(rpid)

    def get(self, rpid):
        'Get data for rpid if it is valid'
        data = self.cache.get(self.get_key(rpid))
        if not self.is_data_valid(data):
            return None
        return data

    @staticmethod
    def is_data_valid(data):
        'Check if cache data is valid'
        if not data:
            return False

        if data.get('v') != settings.CACHE_VERSION:
            return False

        return True

    @staticmethod
    def is_ec2_instance_data_consistent(data, ec2_instance):
        ec2_ip_address = data['ec2_ip_address']
        ec2_instance_status = data['ec2_instance_status']

        if not ec2_instance:
            if ec2_ip_address:
                return False
            else:
                return True

        if ec2_instance_status != ec2_instance.status:
            return False

        if ec2_instance.is_status_temp():
            return False

        if ec2_ip_address != ec2_instance.ip_address:
            return False

        return True

    @classmethod
    def is_data_consistent(cls, data, ec2_instance, lead, raspberry_pi):
        'Check if cache data is consistent against current DB state'
        wrong_password = data['wrong_password']
        lead_status = data['lead_status']
        restart_required = data.get('restart_required', False)
        created = data.get('created')

        if not created:
            return False

        if restart_required != raspberry_pi.restart_required:
            return False

        if not cls.is_ec2_instance_data_consistent(data, ec2_instance):
            return False

        if lead and lead_status != lead.status:
            return False

        if lead and wrong_password != lead.is_wrong_password():
            return False

        return True

    def set(self, rpid, data):
        '''
        Create cache entry for rpid

        *rpid* - rpid string
        *data* - redis-compatible data to set
        '''
        key = self.get_key(rpid)
        self.cache.set(key, data, self.TTL_SECONDS)
        keys = cache.get(self.KEYS, [])
        if key not in keys:
            keys.append(key)
            cache.set(self.KEYS, keys)

    def get_actual_data(self, rpid):
        '''
        Get data for rpid for DB

        *rpid* - rpid string
        '''
        lead_model = apps.get_model('adsrental', 'Lead')
        lead = lead_model.objects.filter(raspberry_pi__rpid=rpid).select_related('ec2instance', 'raspberry_pi').first()
        raspberry_pi = lead and lead.raspberry_pi
        ec2_instance = lead and lead.get_ec2_instance()
        restart_required = raspberry_pi and raspberry_pi.restart_required
        if restart_required:
            raspberry_pi.restart_required = False
            raspberry_pi.save()

        data = {
            'v': self.CACHE_VERSION,
            'created': timezone.now(),
            'rpid': rpid,
            'lead_status': lead and lead.status,
            'wrong_password': lead.is_wrong_password() if lead else False,
            'restart_required': restart_required,
            'ec2_instance_id': ec2_instance and ec2_instance.instance_id,
            'ec2_instance_status': ec2_instance and ec2_instance.status,
            'ec2_hostname': ec2_instance and lead.is_active() and ec2_instance.is_running() and ec2_instance.hostname,
            'ec2_ip_address': ec2_instance and ec2_instance.ip_address,
            'last_ping': None,
        }

        return data

    def delete(self, rpid):
        '''Delete cache data for rpid'''
        key = self.get_key(rpid)
        self.cache.delete(key)
        keys = cache.get(self.KEYS, [])
        if key in keys:
            keys = [i for i in keys if i != key]
            cache.set(self.KEYS, keys)

    def get_data_for_request(self, request):
        '''Get data from cache or db using request.GET'''
        rpid = request.GET.get('rpid', '').strip()
        troubleshoot = request.GET.get('troubleshoot')
        ip_address = request.META.get('REMOTE_ADDR')
        version = request.GET.get('version')
        reported_hostname = request.GET.get('hostname')
        main_tunnel_up = request.GET.get('tunnel_up', '0') == '1'
        reverse_tunnel_up = request.GET.get('reverse_tunnel_up', '1') == '1'
        now = timezone.localtime(timezone.now())

        ping_key = self.get_key(rpid)
        ping_data = cache.get(ping_key)
        if not ping_data:
            ping_data = self.get_actual_data(rpid)
        else:
            if ping_data.get('restart_required'):
                ping_data['restart_required'] = False

        ping_data['ip_address'] = ip_address
        ping_data['reported_hostname'] = reported_hostname
        ping_data['raspberry_pi_version'] = version

        if troubleshoot:
            tunnel_up = main_tunnel_up and reverse_tunnel_up
            ping_data['tunnel_up'] = tunnel_up
            ping_data['last_troubleshoot'] = now

        return ping_data


def generate_password(length=12):
    result = []
    for _ in range(2):
        result.append(secrets.choice(string.digits))
    for _ in range(2):
        result.append(secrets.choice(string.ascii_uppercase))
    for _ in range(length - 4):
        result.append(secrets.choice(string.ascii_lowercase))

    random.shuffle(result)
    return ''.join(result)
