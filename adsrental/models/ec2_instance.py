from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.apps import apps
from django.utils import timezone
import paramiko
import requests

from adsrental.utils import BotoResource


class EC2Instance(models.Model):
    class Meta:
        verbose_name = 'EC2 Instance'
        verbose_name_plural = 'EC2 Instances'

    STATUS_RUNNING = 'running'
    STATUS_STOPPED = 'stopped'
    STATUS_TERMINATED = 'terminated'
    STATUS_PENDING = 'pending'
    STATUS_STOPPING = 'stopping'
    STATUS_MISSING = 'missing'
    STATUS_CHOICES = (
        (STATUS_RUNNING, 'Running', ),
        (STATUS_STOPPED, 'Stopped', ),
        (STATUS_TERMINATED, 'Terminated', ),
        (STATUS_PENDING, 'Pending', ),
        (STATUS_STOPPING, 'Stopping', ),
        (STATUS_MISSING, 'Missing', ),
    )

    instance_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    rpid = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    email = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    lead = models.OneToOneField('adsrental.Lead', blank=True, null=True)
    raspberry_pi = models.OneToOneField('adsrental.RaspberryPi', blank=True, null=True)
    hostname = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=255, db_index=True, default=STATUS_MISSING)
    is_duplicate = models.BooleanField(default=False)
    tunnel_up = models.BooleanField(default=False)
    web_up = models.BooleanField(default=False)
    ssh_up = models.BooleanField(default=False)
    password = models.CharField(max_length=255, default=settings.OLD_EC2_ADMIN_PASSWORD)
    last_synced = models.DateTimeField(default=timezone.now)
    last_troubleshoot = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_boto_instance(self, boto_resource=None):
        if not boto_resource:
            boto_resource = BotoResource().get_resource('ec2')
        instances = boto_resource.instances.filter(
            Filters=[
                {
                    'Name': 'instance-id',
                    'Values': [self.instance_id],
                },
            ],
        )
        for instance in instances:
            return instance

    def update_from_boto(self, boto_instance=None):
        if not boto_instance:
            boto_instance = self.get_boto_instance()
        if not boto_instance:
            self.status = self.STATUS_MISSING
            self.save()
            return

        Lead = apps.get_app_config('adsrental').get_model('Lead')
        tags_changed = False
        rpid = self.get_tag(boto_instance, 'Name')
        lead_email = self.get_tag(boto_instance, 'Email')
        is_duplicate = self.get_tag(boto_instance, 'Duplicate') == 'true'
        lead = Lead.objects.filter(email=lead_email).first() if not is_duplicate else None
        try:
            if lead and lead.ec2instance and lead.ec2instance != self:
                tags_changed = True
                is_duplicate = True
                lead = None
        except EC2Instance.DoesNotExist:
            pass

        self.email = lead_email
        self.rpid = rpid
        self.lead = lead
        self.raspberry_pi = lead and lead.raspberry_pi
        self.is_duplicate = is_duplicate
        self.hostname = boto_instance.public_dns_name
        self.ip_address = boto_instance.public_ip_address
        self.status = boto_instance.state['Name']
        self.last_synced = timezone.now()

        self.save()

        if tags_changed:
            self.set_ec2_tags()

    def __str__(self):
        return '{} ({})'.format(self.instance_id, self.status)

    def get_ssh(self):
        private_key = paramiko.RSAKey.from_private_key_file(settings.FARMBOT_KEY)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.ip_address, username='Administrator', port=40594, pkey=private_key, timeout=20)
        return ssh

    def ssh_execute(self, cmd, input=None, ssh=None):
        if not ssh:
            ssh = self.get_ssh()
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
        if input:
            for line in input:
                ssh_stdin.write('{}\n'.format(line))
                ssh_stdin.flush()
        stderr = ssh_stderr.read()
        stdout = ssh_stdout.read()
        ssh.close()
        return 'OUT: {}\nERR: {}'.format(stdout, stderr)

    @staticmethod
    def get_tag(boto_instance, key):
        if not boto_instance.tags:
            return None

        for tagpair in boto_instance.tags:
            if tagpair['Key'] == key:
                return tagpair['Value']

        return None

    @classmethod
    def upsert_from_boto(cls, boto_instance, instance=None):
        if not instance:
            instance = cls.objects.filter(instance_id=boto_instance.id).first()
        if not instance:
            instance = cls(
                instance_id=boto_instance.id,
            )

        return instance.update_from_boto(boto_instance)

    def terminate(self):
        boto_instance = self.get_boto_instance()
        if not boto_instance:
            self.mark_as_missing()
            return False

        boto_instance.terminate()
        self.status = self.STATUS_TERMINATED
        self.save()
        return True

    def start(self):
        if self.is_duplicate:
            return False
        boto_instance = self.get_boto_instance()
        if not boto_instance:
            self.mark_as_missing()
            return False

        boto_instance.start()
        self.status = self.STATUS_PENDING
        self.save()
        return True

    def stop(self):
        if self.lead:
            return False
        boto_instance = self.get_boto_instance()
        if not boto_instance:
            self.mark_as_missing()
            return False

        boto_instance.stop()
        self.status = self.STATUS_STOPPED
        self.save()
        return True

    def mark_as_missing(self):
        self.status = self.STATUS_MISSING
        self.ssh_up = False
        self.tunnel_up = False
        self.web_up = False
        self.save()

    def troubleshoot(self):
        self.last_troubleshoot = timezone.now()
        boto_instance = self.get_boto_instance()
        if not boto_instance:
            self.mark_as_missing()
            return False

        self.update_from_boto(boto_instance)
        if not self.rpid or not self.rpid.startswith('RP'):
            return False

        self.troubleshoot_status()
        self.troubleshoot_web()
        self.troubleshoot_ssh()
        try:
            self.troubleshoot_proxy()
        except:
            pass
        self.troubleshoot_old_pi_version()
        self.fix_issues()

        self.save()
        return True

    def troubleshoot_status(self):
        Lead = apps.get_app_config('adsrental').get_model('Lead')
        if self.status == self.STATUS_RUNNING:
            if not self.is_duplicate:
                self.stop()
                return
            if not self.lead or self.lead.status == Lead.STATUS_BANNED:
                self.stop()
                return
        if self.status == self.STATUS_STOPPED:
            if not self.is_duplicate and self.lead or self.lead.status != Lead.STATUS_BANNED:
                self.start()
                return

    def troubleshoot_web(self):
        response = None
        try:
            response = requests.get('http://{}:13608'.format(self.hostname), timeout=10)
        except Exception:
            self.web_up = False
            return

        if self.instance_id not in response.text:
            self.web_up = False
            return

        self.web_up = True

    def troubleshoot_ssh(self):
        try:
            output = self.ssh_execute('netstat')
        except:
            self.ssh_up = False
            self.tunnel_up = False
            return

        self.ssh_up = True
        self.tunnel_up = ':2046' in output

    def troubleshoot_proxy(self):
        cmd_to_execute = '''reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable'''
        output = self.ssh_execute(cmd_to_execute)
        if '0x1' in output:
            return

        ssh = self.get_ssh()
        cmd_to_execute = '''reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer /t REG_SZ /d socks=127.0.0.1:3808 /f'''
        ssh.exec_command(cmd_to_execute)
        cmd_to_execute = '''reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyOverride /t REG_SZ /d localhost;127.0.0.1;169.254.169.254; /f'''
        ssh.exec_command(cmd_to_execute)
        cmd_to_execute = '''reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1 /f'''
        ssh.exec_command(cmd_to_execute)
        ssh.close()

    def troubleshoot_old_pi_version(self):
        if not self.raspberry_pi:
            return

        if not self.tunnel_up:
            return

        if self.raspberry_pi.version == settings.OLD_RASPBERRY_PI_VERSION:
            cmd_to_execute = '''ssh pi@localhost -p 2046 "curl https://adsrental.com/static/update_pi.sh | bash"'''
            self.ssh_execute(cmd_to_execute)
            self.raspberry_pi.version = settings.RASPBERRY_PI_VERSION
            self.raspberry_pi.save()

    def troubleshoot_fix(self):
        if not self.raspberry_pi:
            return

        if self.raspberry_pi.version == settings.OLD_RASPBERRY_PI_VERSION:
            return

        if not self.tunnel_up or not self.ssh_up:
            self.raspberry_pi.restart_required = True
            self.raspberry_pi.save()

    def change_password(self):
        if self.password == settings.EC2_ADMIN_PASSWORD:
            return
        try:
            self.ssh_execute('net user Administrator {password}'.format(password=settings.EC2_ADMIN_PASSWORD))
        except:
            raise

        self.password = settings.EC2_ADMIN_PASSWORD
        self.save()

    def set_ec2_tags(self):
        tags = []
        if self.is_duplicate:
            tags.append({'Key': 'Duplicate', 'Value': 'true'})
        if self.email:
            tags.append({'Key': 'Email', 'Value': self.email})
        if self.rpid:
            tags.append({'Key': 'Name', 'Value': self.rpid})
        boto_resource = BotoResource().get_resource('ec2')
        boto_resource.create_tags(Resources=[self.instance_id], Tags=tags)
