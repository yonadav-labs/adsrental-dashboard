from django.db import models


class RaspberryPi(models.Model):
    # owner = models.ForeignKey(Group)  # Reference to tables [Group, User]
    is_deleted = models.BooleanField(verbose_name='Deleted', default=False)
    name = models.CharField(max_length=80, verbose_name='Raspberry Pi ID')
    created_date = models.DateTimeField()
    # created_by = models.ForeignKey('User', related_name='raspberrypi_createdby_set')
    last_modified_date = models.DateTimeField()
    # last_modified_by = models.ForeignKey('User', related_name='raspberrypi_lastmodifiedby_set')
    system_modstamp = models.DateTimeField()
    last_viewed_date = models.DateTimeField(blank=True, null=True)
    last_referenced_date = models.DateTimeField(blank=True, null=True)
    # connection_received = models.ForeignKey(PartnerNetworkConnection, related_name='raspberrypi_connectionreceived_set', blank=True, null=True)
    # connection_sent = models.ForeignKey(PartnerNetworkConnection, related_name='raspberrypi_connectionsent_set', blank=True, null=True)
    version = models.CharField(max_length=255, help_text='DO NOT EDIT', blank=True, null=True)
    tracking_number = models.CharField(db_column='Tracking_Number__c', max_length=255, verbose_name='Tracking Number', blank=True, null=True)
    date_shipped = models.DateField(db_column='Date_Shipped__c', verbose_name='Date Shipped', blank=True, null=True)
    delivery_status = models.TextField(db_column='Delivery_Status__c', verbose_name='Delivery Status', blank=True, null=True)
    last_seen = models.DateTimeField(db_column='Last_Seen__c', verbose_name='Last Seen', blank=True, null=True)
    linked_lead = models.ForeignKey('adsrental.Lead', db_column='Linked_Lead__c', related_name='raspberrypi_linkedlead_set', blank=True, null=True)
    status = models.CharField(max_length=255, choices=[('Available', 'Available'), ('Address Error', 'Address Error'), ('Provisioned', 'Provisioned'), ('Shipped', 'Shipped'), ('Online', 'Online'), ('Offline', 'Offline'), ('Initializing', 'Initializing'), ('Error', 'Error'), ('Banned', 'Banned'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled'), ('Testing', 'Testing')], blank=True, null=True)
    # ec2_instance_id = models.CharField(db_column='EC2_Instance_ID__c', max_length=255, verbose_name='EC2 Instance ID', help_text='DO NOT EDIT!', blank=True, null=True)
    farmbot_active = models.BooleanField(db_column='Farmbot_Active__c', verbose_name='Farmbot Active', help_text='DO NOT EDIT!')
    ignore_city_check = models.BooleanField(db_column='Ignore_City_Check__c', verbose_name='Ignore City Check', help_text='BE CAREFUL USING THIS. REQUIRES REVGO VALIDATION.')
    current_ip_address = models.CharField(db_column='Current_IP_Address__c', max_length=255, verbose_name='Current IP Address', blank=True, null=True)
    current_isp = models.CharField(db_column='Current_ISP__c', max_length=255, verbose_name='Current ISP', blank=True, null=True)
    current_city = models.CharField(db_column='Current_City__c', max_length=255, verbose_name='Current City', blank=True, null=True)
    current_state_region = models.CharField(db_column='Current_State_Region__c', max_length=255, verbose_name='Current State/Region', blank=True, null=True)
    current_country = models.CharField(db_column='Current_Country__c', max_length=255, verbose_name='Current Country', blank=True, null=True)
    status_message = models.TextField(db_column='Status_Message__c', verbose_name='Status Message', blank=True, null=True)
    rev_go_shipment_id = models.CharField(db_column='RevGo_Shipment_ID__c', max_length=255, verbose_name='RevGo Shipment ID', blank=True, null=True)
    rev_go_feedback = models.CharField(db_column='RevGo_Feedback__c', max_length=255, verbose_name='RevGo Feedback', blank=True, null=True)
    first_seen = models.DateTimeField(db_column='First_Seen__c', verbose_name='First Seen', blank=True, null=True)
    ignore_location_check = models.BooleanField(db_column='Ignore_Location_Check__c', verbose_name='Ignore Location Check', help_text='NEVER USE WITHOUT SUPREME APPROVAL!!!!!!')
    comment = models.TextField(blank=True, null=True)
    ec2_instance = models.ForeignKey('adsrental.Ec2Instance', db_column='EC2_Instance__c', blank=True, null=True)
    online = models.BooleanField()
    tunnel_last_tested = models.DateTimeField(db_column='Tunnel_Last_Tested__c', verbose_name='Tunnel Last Tested', blank=True, null=True)
    tunnel_online = models.BooleanField(db_column='Tunnel_Online__c', verbose_name='Tunnel Online')
    usps_tracking_code = models.CharField(db_column='USPS_Tracking_Code__c', max_length=255, verbose_name='USPS Tracking Code', blank=True, null=True)
    logfile_url = models.CharField(db_column='Logfile_Url__c', max_length=1300, verbose_name='Logfile Url', blank=True, null=True)
    rdp = models.CharField(db_column='RDP__c', max_length=1300, verbose_name='RDP', blank=True, null=True)
    location_match = models.BooleanField(db_column='Location_Match__c', verbose_name='Location Match')
    tested_internal = models.BooleanField(db_column='Tested_Internal__c', verbose_name='Tested Internal')
    usps_feedback = models.TextField(db_column='USPS_Feedback__c', verbose_name='USPS Feedback', blank=True, null=True)
    tested = models.BooleanField()
    config_file_download = models.CharField(db_column='Config_File_Download__c', max_length=1300, verbose_name='Config File Download', blank=True, null=True)
    rp_status = models.CharField(db_column='RP_Status__c', max_length=255, verbose_name='RP Status', choices=[('Offline', 'Offline'), ('Online', 'Online')], blank=True, null=True)
    delivered_internal = models.BooleanField(db_column='Delivered_Internal__c', verbose_name='Delivered Internal')
    delivered = models.BooleanField()

    class Meta():
        db_table = 'Raspberry_Pi__c'
        verbose_name = 'Raspberry Pi'
        verbose_name_plural = 'Raspberry Pis'
        # keyPrefix = 'a02'
