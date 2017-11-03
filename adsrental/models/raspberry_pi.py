from django.db import models


class RaspberryPi(models.Model):
    class Meta:
        verbose_name = 'Raspberry PI'
        verbose_name_plural = 'Raspberry PIs'

    name = models.CharField(max_length=255, db_column='Name', db_index=True)
    comment = models.TextField(db_column='Comment__c', null=True, blank=True)
    config_file_download = models.TextField(db_column='Config_File_Download__c', null=True, blank=True)
    current_city = models.CharField(max_length=255, db_column='Current_City__c', null=True, blank=True)
    current_ip_address = models.CharField(max_length=255, db_column='Current_IP_Address__c', null=True, blank=True)
    current_isp = models.CharField(max_length=255, db_column='Current_ISP__c', null=True, blank=True)
    current_state_region = models.CharField(max_length=255, db_column='Current_State_Region__c', null=True, blank=True)
    date_shipped = models.DateField(db_column='Date_Shipped__c', null=True, blank=True)
    delivered_internal = models.BooleanField(db_column='Delivered__c', default=False)
    delivered_status = models.TextField(db_column='Delivery_Status__c', null=True, blank=True)
    ec2_instance = models.ForeignKey('EC2Instance', null=True, blank=True)

    def __str__(self):
        return self.name
