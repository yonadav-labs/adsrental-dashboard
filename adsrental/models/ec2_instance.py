from django.db import models

from salesforce_handler.models import Ec2Instance as SFEc2Instance


class Ec2Instance(models.Model):
    salesforce_id = models.CharField(max_length=255, db_index=True, null=True)
    # owner = models.ForeignKey('Group', models.DO_NOTHING)  # Reference to tables [Group, User]
    is_deleted = models.BooleanField(verbose_name='Deleted', default=False)
    name = models.CharField(max_length=80, blank=True, null=True)
    created_date = models.DateTimeField()
    # created_by = models.ForeignKey('User', models.DO_NOTHING, related_name='ec2instance_createdby_set', )
    last_modified_date = models.DateTimeField()
    # last_modified_by = models.ForeignKey('User', models.DO_NOTHING, related_name='ec2instance_lastmodifiedby_set', )
    system_modstamp = models.DateTimeField()
    last_viewed_date = models.DateTimeField(blank=True, null=True)
    last_referenced_date = models.DateTimeField(blank=True, null=True)
    # connection_received = models.ForeignKey('PartnerNetworkConnection', models.DO_NOTHING, related_name='ec2instance_connectionreceived_set', blank=True, null=True)
    # connection_sent = models.ForeignKey('PartnerNetworkConnection', models.DO_NOTHING, related_name='ec2instance_connectionsent_set', blank=True, null=True)
    hostname = models.CharField(max_length=255, blank=True, null=True)
    instance_id = models.CharField(db_column='Instance_ID__c', max_length=255, verbose_name='Instance ID', blank=True, null=True)

    class Meta():
        db_table = 'EC2_Instance__c'
        verbose_name = 'EC2 Instance'
        verbose_name_plural = 'EC2 Instances'
        # keyPrefix = 'a04'

    @classmethod
    def upsert_from_sf(cls, instance):
        item, created = cls.objects.update_or_create(
            salesforce_id=instance.id,
            defaults=dict(
                is_deleted=instance.is_deleted,
                name=instance.name,
                created_date=instance.created_date,
                last_modified_date=instance.last_modified_date,
                system_modstamp=instance.system_modstamp,
                last_viewed_date=instance.last_viewed_date,
                last_referenced_date=instance.last_referenced_date,
                hostname=instance.hostname,
                instance_id=instance.instance_id,
            ),
        )
        item.save()
        return item

    def upsert_to_sf(self):
        item, created = SFEc2Instance.objects.update_or_create(
            salesforce_id=self.id,
            defaults=dict(
                is_deleted=self.is_deleted,
                name=self.name,
                created_date=self.created_date,
                last_modified_date=self.last_modified_date,
                system_modstamp=self.system_modstamp,
                last_viewed_date=self.last_viewed_date,
                last_referenced_date=self.last_referenced_date,
                hostname=self.hostname,
                instance_id=self.instance_id,
            ),
        )
        item.save()
        return item
