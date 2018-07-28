import json

from django.db import models
from django.conf import settings
from django_bulk_update.manager import BulkUpdateManager
import vultr


class VultrInstance(models.Model):
    """
    Stores a single Vultr Instance entry.
    Currently only instances with tag Web are allowed
    """
    USERNAME = 'Administrator'
    TAGS = ('Web', )
    RDP_PORT = 3389

    id = models.AutoField(primary_key=True)
    instance_id = models.PositiveIntegerField(blank=True, null=True, db_index=True, help_text='Vultr ID.')
    label = models.CharField(max_length=255, help_text='Label field from Vultr')
    os = models.CharField(max_length=255, help_text='OS field from Vultr')
    ip_address = models.CharField(max_length=50, help_text='Main IP field from Vultr')
    status = models.CharField(max_length=20, help_text='Power status field from Vultr')
    password = models.CharField(max_length=255, help_text='Default password field from Vultr')
    tag = models.CharField(max_length=255, help_text='Tag field from Vultr')
    data = models.TextField(help_text='Full data from Vultr')
    objects = BulkUpdateManager()

    def is_running(self):
        return self.status == 'running'

    @classmethod
    def update_all_from_vultr(cls, instance_id=None):
        vultr_client = vultr.Vultr(settings.VULTR_API_KEY)
        for tag in cls.TAGS:
            for new_instance_id, data in vultr_client.server.list(params=dict(tag=tag)).items():
                new_instance_id = int(new_instance_id)
                if instance_id and instance_id != new_instance_id:
                    continue

                cls.objects.update_or_create(instance_id=new_instance_id, defaults=dict(
                    label=data['label'],
                    os=data['os'],
                    status=data['power_status'],
                    ip_address=data['main_ip'],
                    password=data['default_password'],
                    tag=data['tag'],
                    data=json.dumps(data),
                ))

    def update_from_vultr(self):
        VultrInstance.update_all_from_vultr(self.instance_id)

    def get_windows_rdp_uri(self):
        return 'rdp://{}:{}:{}:{}'.format(self.ip_address, self.RDP_PORT, self.USERNAME, self.password)

    def get_rdp_uri(self):
        return 'rdp://full%20address=s:{}:{}&username=s:{}'.format(self.ip_address, self.RDP_PORT, self.USERNAME)

    def get_web_rdp_link(self):
        return 'http://{host}:{rdp_client_port}/#host={hostname}&port={port}&user={user}&password={password}&rpid={rpid}&connect=true'.format(
            host=settings.HOSTNAME,
            rdp_client_port=9999,
            port=self.RDP_PORT,
            hostname=self.ip_address,
            user=self.USERNAME,
            password=self.password,
            rpid='Vultr{}'.format(self.instance_id),
        )