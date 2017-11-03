from django.db import models


class EC2Instance(models.Model):
    class Meta:
        verbose_name = 'EC2 Instance'
        verbose_name_plural = 'EC2 Instances'

    name = models.CharField(max_length=255, db_column='Name', db_index=True)
    hostname = models.CharField(max_length=255, db_column='Hostname__c', db_index=True)
    instance_id = models.CharField(max_length=255, db_column='Instance_ID__c', db_index=True)

    def __str__(self):
        return self.name
