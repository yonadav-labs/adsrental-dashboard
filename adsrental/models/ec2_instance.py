import socket
import datetime
import time

from django.db import models
from django.conf import settings
from django.apps import apps
from django.utils import timezone
from django_bulk_update.manager import BulkUpdateManager
import paramiko

from adsrental.utils import BotoResource, PingCacheHelper


class SSHConnectException(Exception):
    pass


class EC2Instance(models.Model):
    """
    Stores a single EC2 Instance entry, related to :model:`adsrental.Lead`. It does not have direct connection to
    :model:`adsrental.RaspberryPi`, but it always can be obtained from related Lead.

    It is created automatically when you use *Mark as Qualified, Assign RPi, create Shipstation order* action in Lead admin.

    **How to use EC2 RDP**

    You can connect to EC2 Instance using RDP. EC2 has Antidetect browser, that you can launch from desktop *Browser.exe*

    To connect to RDP:

    1. click on *RDP* link in *Links* column. In downloads you see file *RP<numbers>.rdp*.
    2. Open this file by double-click with your favorite RDP manager.
    3. Use *Browser.exe* for Antidetect or *Firefox* for browsing
    4. You should be able to connect. If you cannot - read the following troubleshooting guide.

    **I cannot connect to RDP**

    Looks like EC2 is stopped, not responding, or you are using old *RP<number>.rdp* file

    1. Download new *RP<number>.rdp* file by clicking *RDP* link
    2. If you still cannot connect check if EC2 status is running. If it is not - report to me. Probably lead is banned.
    3. If statu is Running, but you still cannot connect - use *Stop* admin action for this EC2. It will start on next ping for RaspberryPi.

    **I get Proxy Error while trying to connect to internet**

    There could be several reasons, but short explanation is - reverse tunnel is down.

    What to do:

    1. Check if RPi online is green. If it is not - device is turned off, so proxy does not work. Ask user to check his device and if green LED is blinking.
    2. Check Tunnel up column. If it is *Yes* then just wait. RaspberryPi device tries to revive tunnel every 10 minutes and it works in 95% of cases.
    3. If you waited longer than 10 minutes and tunnel is still down, choose *Stop* action for this EC2.
       Tunnel should be up once EC2 restarts. Takes 1-10 minutes.

    **I see black window when I connect to EC2**

    Close it. Newest RaspberryPi devices do not use this ruby webservice anymore.
    """

    class Meta:
        verbose_name = 'EC2 Instance'
        verbose_name_plural = 'EC2 Instances'

    TUNNEL_UP_TTL_SECONDS = 20 * 60

    R53_HOST = 'adsrentalswarm.click'
    R53_ZONE_ID = settings.AWS_R53_ZONE_ID

    STATUS_RUNNING = 'running'
    STATUS_STOPPED = 'stopped'
    STATUS_TERMINATED = 'terminated'
    STATUS_PENDING = 'pending'
    STATUS_STOPPING = 'stopping'
    STATUS_MISSING = 'missing'
    STATUS_SHUTTING_DOWN = 'shutting-down'
    STATUS_CHOICES = (
        (STATUS_RUNNING, 'Running', ),
        (STATUS_STOPPED, 'Stopped', ),
        (STATUS_TERMINATED, 'Terminated', ),
        (STATUS_PENDING, 'Pending', ),
        (STATUS_STOPPING, 'Stopping', ),
        (STATUS_MISSING, 'Missing', ),
        (STATUS_SHUTTING_DOWN, 'Shutting down', ),
    )
    STATUSES_ACTIVE = [STATUS_RUNNING, STATUS_STOPPED, STATUS_PENDING, STATUS_STOPPING]

    instance_id = models.CharField(max_length=255, blank=True, null=True, db_index=True, help_text='AWS EC2 ID.')
    rpid = models.CharField(max_length=255, blank=True, null=True, db_index=True, help_text='RPID that was inserted to EC2 metadata')
    email = models.CharField(max_length=255, blank=True, null=True, db_index=True, help_text='Lead email')
    lead = models.OneToOneField('adsrental.Lead', blank=True, null=True, help_text='Corresponding lead', on_delete=models.SET_NULL)
    hostname = models.CharField(
        max_length=255, blank=True, null=True, help_text='Public EC2 hostname. Updates everytime EC2 restarts. RPi use it to create tunnels.',
    )
    ip_address = models.CharField(max_length=255, blank=True, null=True, help_text='Public EC2 IP. Updates everytime EC2 restarts.')
    status = models.CharField(choices=STATUS_CHOICES, max_length=255, db_index=True, default=STATUS_MISSING, help_text='Status of EC2, same as in AWS UI')
    is_duplicate = models.BooleanField(default=False, help_text='Obsolete field')
    tunnel_up_date = models.DateTimeField(blank=True, null=True, help_text='Last time both tunnel and reverse tunnels were online. Chcecked every 10 minutes.')
    password = models.CharField(max_length=255, default=settings.EC2_ADMIN_PASSWORD, help_text='Password for RDP session')
    last_synced = models.DateTimeField(default=timezone.now, help_text='Last time when instance state was synced back from AWS')
    last_troubleshoot = models.DateTimeField(blank=True, null=True, help_text='Last time RaspberryPi tested tunnels. Should be updated every 10 minutes if device is online and up-to-date.')
    version = models.CharField(max_length=255, default=settings.EC2_VERSION, help_text='AWS EC2 Firmware version')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = BulkUpdateManager()

    @classmethod
    def launch_for_lead(cls, lead):
        '''
        Launch EC2, set tags if it does not exist. If it exists - make sure it is Running.
        '''
        if not settings.MANAGE_EC2:
            return False

        if not lead.raspberry_pi:
            return None
        instance = cls.objects.filter(lead=lead).first()
        if instance:
            instance.update_from_boto(instance.get_boto_instance())
            if instance.status == EC2Instance.STATUS_STOPPED:
                instance.is_duplicate = False
                instance.lead = lead
                instance.email = lead.email
                instance.set_ec2_tags()
                instance.save()
                instance.start()

            return instance

        rpid = lead.raspberry_pi.rpid
        instance = cls.objects.filter(rpid=rpid, status__in=cls.STATUSES_ACTIVE).first()
        if instance:
            instance.update_from_boto(instance.get_boto_instance())
            instance.is_duplicate = False
            instance.lead = lead
            instance.email = lead.email
            instance.set_ec2_tags()
            instance.save()
            instance.start()
            return instance

        return BotoResource().launch_instance(lead.raspberry_pi.rpid, lead.email)

    def get_boto_instance(self, boto_resource=None):
        '''
        Get dict with data from AWS about current instance.

        *boto_instance* - if provided, use provided data instead of getting it from AWS.
        '''
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

    def is_status_temp(self):
        '''
        Check if status is not *Stopping* or *Pending*
        '''
        return self.status in [self.STATUS_PENDING, self.STATUS_STOPPING]

    @classmethod
    def is_status_active(cls, status):
        '''
        Check if status is not *Stopped* or *Terminated*
        '''
        return status in cls.STATUSES_ACTIVE

    def is_active(self):
        '''
        Check if instance status is not *Stopped* or *Terminated*
        '''
        return self.status in self.STATUSES_ACTIVE

    def is_running(self):
        '''
        Check if instance status is *Running*
        '''
        return self.status == self.STATUS_RUNNING

    @classmethod
    def is_status_running(cls, status):
        '''
        Check if status is *Running*
        '''
        return status == cls.STATUS_RUNNING

    def is_stopped(self):
        '''
        Check if instance status is *Stopped*
        '''
        return self.status == self.STATUS_STOPPED

    def is_tunnel_up(self):
        '''
        Check if tunnels were reported as UP in last 20 minutes.
        '''
        if not self.tunnel_up_date:
            return False
        now = timezone.now()
        return self.tunnel_up_date > now - datetime.timedelta(seconds=self.TUNNEL_UP_TTL_SECONDS)

    def update_from_boto(self, boto_instance=None):
        '''
        Update tags and state from AWS.

        *boto_instance* - if provided, use provided data instead of getting it from AWS.
        '''
        if not boto_instance:
            boto_instance = self.get_boto_instance()
        if not boto_instance:
            self.status = self.STATUS_MISSING
            self.save()
            return self

        lead_model = apps.get_app_config('adsrental').get_model('Lead')
        tags_changed = False
        rpid = self.get_tag(boto_instance, 'Name')
        lead_email = self.get_tag(boto_instance, 'Email')
        is_duplicate = self.get_tag(boto_instance, 'Duplicate') == 'true'
        self.status = boto_instance.state['Name']
        is_active = self.is_active()

        lead = lead_model.objects.filter(raspberry_pi__rpid=rpid).first() if is_active else None

        self.email = lead_email
        self.rpid = rpid
        self.lead = lead
        self.is_duplicate = is_duplicate
        if self.is_running():
            self.hostname = boto_instance.public_dns_name
            self.ip_address = boto_instance.public_ip_address
        self.last_synced = timezone.now()

        self.save()

        if tags_changed:
            self.set_ec2_tags()

        return self

    def __str__(self):
        return self.instance_id

    def get_ssh(self):
        '''
        Create SSH connection to EC2
        '''
        private_key = paramiko.RSAKey.from_private_key_file(settings.FARMBOT_KEY)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh.connect(self.ip_address, username='Administrator', port=40594, pkey=private_key, timeout=20)
        except (paramiko.ssh_exception.SSHException, EOFError, socket.timeout):
            raise SSHConnectException('Cannot connect, EC2 SSH is down')

        return ssh

    def ssh_execute(self, cmd, input_list=None, ssh=None, blocking=True):
        '''
        Safe execute SSH command on EC2 and get output.
        '''
        if not ssh:
            ssh = self.get_ssh()

        try:
            ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd, timeout=20)
        except (paramiko.ssh_exception.SSHException, EOFError, socket.timeout):
            raise SSHConnectException('Cannot connect, EC2 SSH is down')
        if input_list:
            for line in input_list:
                ssh_stdin.write('{}\n'.format(line))
                ssh_stdin.flush()
        if blocking:
            try:
                stderr = ssh_stderr.read()
                stdout = ssh_stdout.read()
            except socket.timeout:
                return ''
            ssh.close()
            return 'OUT: {}\nERR: {}'.format(stdout.decode(), stderr.decode())

        return True

    @staticmethod
    def get_tag(boto_instance, key):
        '''
        Get AWS EC2 instance tag value.
        '''
        if not boto_instance.tags:
            return None

        for tagpair in boto_instance.tags:
            if tagpair['Key'] == key:
                return tagpair['Value']

        return None

    @classmethod
    def upsert_from_boto(cls, boto_instance, instance=None):
        '''
        Create or update instance from AWS using *instance_id* as a key.
        '''
        if not instance:
            instance = cls.objects.filter(instance_id=boto_instance.id).first()
        if not instance:
            instance = cls(
                instance_id=boto_instance.id,
            )

        return instance.update_from_boto(boto_instance)

    def terminate(self):
        '''
        Terminate instance. Terminated instance can stay up for 24 hours in AWS.
        '''
        boto_instance = self.get_boto_instance()
        if not boto_instance:
            self.mark_as_missing()
            return False

        boto_instance.terminate()
        self.status = self.STATUS_TERMINATED
        self.lead = None
        self.rpid = None
        self.save()
        return True

    def start(self, blocking=False):
        '''
        Start stopped EC2 instance.

        *blocking* - waits until instance enters *Running* state.
        '''
        if not settings.MANAGE_EC2:
            return False
        boto_instance = self.get_boto_instance()
        self.update_from_boto(boto_instance)
        if self.status != self.STATUS_STOPPED:
            return False

        self.status = self.STATUS_PENDING
        self.save()
        boto_instance.start()
        if blocking:
            while True:
                boto_instance = self.get_boto_instance()
                status = boto_instance.state['Name']
                if status == self.STATUS_RUNNING:
                    self.update_from_boto(boto_instance)
                    break
                time.sleep(10)

        return True

    def restart(self):
        'Restart instance. DO not use, as it can take up to 10 minutes.'
        if not settings.MANAGE_EC2:
            return False
        self.stop(blocking=True)
        self.start(blocking=True)
        return True

    def stop(self, blocking=False):
        '''
        Stop running or pending EC2 instance.

        *blocking* - waits until instance enters *Stopped* state.
        '''
        if not settings.MANAGE_EC2:
            return False
        boto_instance = self.get_boto_instance()
        self.update_from_boto(boto_instance)
        if self.status not in (self.STATUS_RUNNING, self.STATUS_PENDING):
            return False

        self.status = self.STATUS_STOPPING
        self.hostname = None
        self.ip_address = None
        self.save()
        boto_instance.stop()
        if blocking:
            while True:
                boto_instance = self.get_boto_instance()
                status = boto_instance.state['Name']
                if status == self.STATUS_STOPPED:
                    self.update_from_boto(boto_instance)
                    break
                time.sleep(10)

        return True

    def mark_as_missing(self):
        'Mark instance that not present in AWS.'
        self.status = self.STATUS_MISSING
        self.tunnel_up_date = None
        self.save()

    def troubleshoot(self):
        'Run all troubleshoot at once.'
        self.last_troubleshoot = timezone.now()
        boto_instance = self.get_boto_instance()
        if not boto_instance:
            self.mark_as_missing()
            return False

        self.update_from_boto(boto_instance)
        if not self.rpid or not self.rpid.startswith('RP'):
            return False

        self.troubleshoot_status()
        self.troubleshoot_proxy()

        self.save()
        return True

    def troubleshoot_status(self):
        'Check and fix if instance is running for active lead and stopped for banned lead'
        if self.status == self.STATUS_RUNNING:
            if not self.lead.is_active():
                # self.stop()
                return
        if self.status == self.STATUS_STOPPED:
            if self.lead and self.lead.is_active():
                self.start()
                return

    def troubleshoot_proxy(self):
        'Check and fix proxy settings. Makes sure that web can be reached only via proxy tunnel.'
        cmd_to_execute = 'reg query "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable'
        output = self.ssh_execute(cmd_to_execute)
        if '0x1' in output:
            return

        ssh = self.get_ssh()
        cmd_to_execute = 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyServer /t REG_SZ /d socks=127.0.0.1:3808 /f'
        ssh.exec_command(cmd_to_execute)
        cmd_to_execute = 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyOverride /t REG_SZ /d localhost;127.0.0.1;169.254.169.254; /f'
        ssh.exec_command(cmd_to_execute)
        cmd_to_execute = 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1 /f'
        ssh.exec_command(cmd_to_execute)
        ssh.close()

    def troubleshoot_old_pi_version(self):
        'Force update old version that do no support firmware update.'
        if not self.lead or not self.lead.raspberry_pi:
            return

        if self.tunnel_up_date is None:
            return

        raspberry_pi = self.lead.raspberry_pi

        if raspberry_pi.version == settings.OLD_RASPBERRY_PI_VERSION:
            cmd_to_execute = '''ssh pi@localhost -p 2046 "curl https://adsrental.com/static/update_pi.sh | bash"'''
            self.ssh_execute(cmd_to_execute)
            raspberry_pi.save()

    def change_password(self, password=None):
        'Obsolete method. Was used to update all old non-human-friendly passwords.'
        if password is None:
            password = self.password


        output = self.ssh_execute('net user Administrator {password}'.format(password=password))
        if 'successfully' not in output:
            raise ValueError(output)

        self.password = password
        self.save()


    def set_ec2_tags(self):
        'Update RPID and email in EC2 metadata on AWS.'
        tags = []
        if self.is_duplicate:
            tags.append({'Key': 'Duplicate', 'Value': 'true'})
        if self.email:
            tags.append({'Key': 'Email', 'Value': self.email})
        if self.rpid:
            tags.append({'Key': 'Name', 'Value': self.rpid})
        boto_resource = BotoResource().get_resource('ec2')
        boto_resource.create_tags(Resources=[self.instance_id], Tags=tags)

    def clear_ping_cache(self):
        'Delete cache for this instance RPID.'
        PingCacheHelper().delete(self.rpid)

    def get_r53_hostname(self):
        return '{}.{}'.format(self.rpid, self.R53_HOST)

    def get_windows_rdp_uri(self):
        return 'rdp://{}:{}:{}:{}'.format(self.hostname, 23255, 'Administrator', self.password)

    def get_rdp_uri(self):
        return 'rdp://full%20address=s:{}:{}&username=s:{}'.format(self.hostname, 23255, 'Administrator')

    def get_web_rdp_link(self):
        return 'http://{host}:{rdp_client_port}/#host={hostname}&user={user}&password={password}&rpid={rpid}&connect=true'.format(
            host=settings.HOSTNAME,
            rdp_client_port=9999,
            hostname=self.hostname,
            user='Administrator',
            password=self.password,
            rpid=self.rpid,
        )
