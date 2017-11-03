from django.db import models

from adsrental.models.ec2_instance import EC2Instance


class RaspberryPi(models.Model):
    class Meta:
        verbose_name = 'Raspberry PI'
        verbose_name_plural = 'Raspberry PIs'

    salesforce_id = models.CharField(max_length=255, db_index=True, null=True)
    name = models.CharField(max_length=255, db_column='Name', db_index=True)
    comment = models.TextField(db_column='Comment__c', null=True, blank=True)
    version = models.TextField(null=True, blank=True)
    config_file_download = models.TextField(db_column='Config_File_Download__c', null=True, blank=True)
    current_city = models.CharField(max_length=255, db_column='Current_City__c', null=True, blank=True)
    current_ip_address = models.CharField(max_length=255, db_column='Current_IP_Address__c', null=True, blank=True)
    current_isp = models.CharField(max_length=255, db_column='Current_ISP__c', null=True, blank=True)
    current_state_region = models.CharField(max_length=255, db_column='Current_State_Region__c', null=True, blank=True)
    date_shipped = models.DateField(db_column='Date_Shipped__c', null=True, blank=True)
    delivered_internal = models.BooleanField(db_column='Delivered__c', default=False)
    delivery_status = models.TextField(db_column='Delivery_Status__c', null=True, blank=True)
    ec2_instance = models.ForeignKey(EC2Instance, null=True, blank=True)
    is_deleted = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @classmethod
    def upsert_from_sf(cls, data):
        item, created = cls.objects.update_or_create(
            salesforce_id=data['ID'],
            defaults=dict(
                name=data['NAME'],
                comment=data['COMMENT__C'],
                version=data['VERSION__C'],
                config_file_download=data['CONFIG_FILE_DOWNLOAD__C'],
                current_city=data['CURRENT_CITY__C'],
                current_ip_address=data['CURRENT_IP_ADDRESS__C'],
                current_isp=data['CURRENT_ISP__C'],
                current_state_region=data['CURRENT_STATE_REGION__C'],
                date_shipped=data['DATE_SHIPPED__C'] or None,
                delivered_internal=data['DELIVERED_INTERNAL__C'] == 'true',
                delivery_status=data['DELIVERY_STATUS__C'],
                ec2_instance=EC2Instance.objects.filter(salesforce_id=data['EC2_INSTANCE_ID__C']).first(),
                is_deleted=data['ISDELETED'] == 'true',
            ),
        )
        item.save()

# {
#     'REVGO_FEEDBACK__C': '',
#     'LASTMODIFIEDDATE': '2017-09-06T02:52:00.000Z',
#     'CURRENT_STATE_REGION__C': 'Texas (TX)',
#     'LASTMODIFIEDBYID': '00546000000rlLVAAY',
#     'CURRENT_IP_ADDRESS__C': '73.166.155.174',
#     'USPS_FEEDBACK__C': '',
#     'IGNORE_CITY_CHECK__C': 'false',
#     'TUNNEL_LAST_TESTED__C': '',
#     'FIRST_SEEN__C': '2017-06-21T14:00:19.000Z',
#     'CONNECTIONSENTID': '',
#     'CURRENT_CITY__C': 'Houston',
#     'ISDELETED': 'false',
#     'CONFIG_FILE_DOWNLOAD__C': '<a href="https://adsrental.com/SF/download_config_file.php?rpid=RP-00000001" target="_blank">RP-00000001</a>',
#     'USPS_TRACKING_CODE__C': '',
#     'COMMENT__C': '',
#     'VERSION__C': '1.2.11',
#     'DELIVERY_STATUS__C': '',
#     'LAST_SEEN__C': '2017-07-25T22:04:00.000Z',
#     'CURRENT_ISP__C': 'Comcast Cable',
#     'LINKED_LEAD__C': '00Q46000003r2pAEAQ',
#     'SYSTEMMODSTAMP': '2017-09-21T07:34:31.000Z',
#     'LASTREFERENCEDDATE': '',
#     'OWNERID': '00546000000rlLVAAY',
#     'CONNECTIONRECEIVEDID': '',
#     'RP_STATUS__C': '',
#     'CURRENT_COUNTRY__C': 'United States (US)',
#     'EC2_INSTANCE_ID__C': 'i-01cacd76b8e526ae9',
#     'TUNNEL_ONLINE__C': 'false',
#     'DATE_SHIPPED__C': '',
#     'REVGO_SHIPMENT_ID__C': '',
#     'CREATEDDATE': '2017-05-18T19:07:40.000Z',
#     'LASTVIEWEDDATE': '',
#     'ID': 'a0246000001uLhzAAE',
#     'LOGFILE_URL__C': '<a href="https://adsrental.com/log/RP-00000001" target="_blank">https://adsrental.com/log/RP-00000001</a>',
#     'TESTED_INTERNAL__C': 'false',
#     'DELIVERED_INTERNAL__C': 'false',
#     'STATUS__C': 'Offline',
#     'TRACKING_NUMBER__C': '',
#     'NAME': 'RP-00000001',
#     'IGNORE_LOCATION_CHECK__C': 'false',
#     'DELIVERED__C': 'false',
#     'FARMBOT_ACTIVE__C': 'false',
#     'RDP__C': '<a href="https://adsrental.com/rdp.php?i=RP-00000001&amp;h=" target="_blank"> </a>',
#     'CREATEDBYID': '00546000000rlLVAAY',
#     'LOCATION_MATCH__C': 'true',
#     'EC2_INSTANCE__C': '',
#     'TESTED__C': 'false',
#     'ONLINE__C': 'false',
#     'STATUS_MESSAGE__C': ''
# }
