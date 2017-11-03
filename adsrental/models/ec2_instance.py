from django.db import models


class EC2Instance(models.Model):
    class Meta:
        verbose_name = 'EC2 Instance'
        verbose_name_plural = 'EC2 Instances'

    salesforce_id = models.CharField(max_length=255, db_index=True, null=True)
    name = models.CharField(max_length=255, db_column='Name', db_index=True)
    hostname = models.CharField(max_length=255, db_column='Hostname__c', db_index=True)
    instance_id = models.CharField(max_length=255, db_column='Instance_ID__c', db_index=True)
    owner_id = models.CharField(max_length=255, null=True, blank=True)
    created_date = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @classmethod
    def upsert_from_sf(cls, data):
        item, created = cls.objects.update_or_create(
            salesforce_id=data['ID'],
            defaults=dict(
                name=data['NAME'],
                hostname=data['HOSTNAME__C'],
                instance_id=data['INSTANCE_ID__C'],
                owner_id=data['OWNERID'],
                created_date=data['CREATEDDATE'],
                is_deleted=data['ISDELETED'] == 'true',
            ),
        )
        item.save()

# {
#     'NAME': 'WP00000001',
#     'LASTMODIFIEDDATE': '2017-08-03T03:18:51.000Z',
#     'LASTREFERENCEDDATE': '',
#     'LASTMODIFIEDBYID': '00546000000rlLVAAY',
#     'CONNECTIONSENTID': '',
#     'INSTANCE_ID__C': 'i-03f82ea7b94a30c75',
#     'CREATEDBYID': '00546000000rlLVAAY',
#     'SYSTEMMODSTAMP': '2017-08-04T10:36:30.000Z',
#     'CONNECTIONRECEIVEDID': '',
#     'CREATEDDATE': '2017-07-24T22:09:39.000Z',
#     'OWNERID': '00546000000rlLVAAY',
#     'LASTVIEWEDDATE': '',
#     'ID': 'a0446000003H4V5AAK',
#     'ISDELETED': 'false',
#     'HOSTNAME__C': 'ec2-54-200-52-65.us-west-2.compute.amazonaws.com'
# }
