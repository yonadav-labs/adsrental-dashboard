from django.core.management.base import BaseCommand
from django.conf import settings
import boto3
import paramiko
import requests

from adsrental.models.lead import Lead


class Command(BaseCommand):
    help = 'Check tunnel states for EC2'
    ec2_max_results = 50

    def add_arguments(self, parser):
        parser.add_argument('--emails')
        parser.add_argument('--execute', action='store_true')
        parser.add_argument('--update', action='store_true')
        parser.add_argument('--fix-proxy', action='store_true')

    def get_instance_tag(self, instance, key):
        if not instance.tags:
            return None

        for tagpair in instance.tags:
            if tagpair['Key'] == key:
                return tagpair['Value']

        return None

    def handle(
        self,
        emails,
        execute,
        update,
        fix_proxy,
        **kwargs
    ):
        boto_client = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        ).resource('ec2', region_name=settings.AWS_REGION)
        print 'Starting...'

        private_key = paramiko.RSAKey.from_private_key_file("/app/cert/farmbot.pem")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        instances = boto_client.instances.filter(
            MaxResults=self.ec2_max_results,
        )

        leads = Lead.objects.filter(
            raspberry_pi__isnull=False,
            status=Lead.STATUS_QUALIFIED,
            # raspberry_pi__last_seen__gt=timezone.now() - datetime.timedelta(hours=1),
            email__in=emails.split(','),
        ).select_related('raspberry_pi').order_by('email')
        print len(leads), emails.split(',')
        for lead in leads:
            print lead, lead.email
            instances = boto_client.instances.filter(
                Filters=[
                    {
                        'Name': 'tag:Email',
                        'Values': [lead.email],
                    },
                ],
            )
            instance = None
            for i in instances:
                instance = i

            if instance is None:
                print 'NO_EC2:', lead.email
                continue

            public_dns_name = instance.public_dns_name
            instance_rpid = self.get_instance_tag(instance, 'Name')
            instance_email = self.get_instance_tag(instance, 'Email')
            instance_state = instance.state['Name']

            if instance_state != 'running':
                continue

            if not instance_rpid or not instance_rpid.startswith('RP'):
                continue

            response = None
            try:
                response = requests.get('http://{}:13608'.format(public_dns_name), timeout=10)
            except Exception as e:
                print 'EC2_WEB_DOWN:', instance_rpid, instance_email, public_dns_name, ':', e

            if response and instance.id not in response.text:
                print 'EC2_WEB_INVALID:', instance_rpid, instance_email, public_dns_name, ':', response.text, 'instead of', instance.id

            # print 'CONNECTING:', instance_rpid, instance_email, public_dns_name
            cmd_to_execute = 'netstat'
            try:
                ssh.connect(public_dns_name, username='Administrator', port=40594, pkey=private_key, timeout=5)
                ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_to_execute)

            except Exception as e:
                print 'SSH_DOWN:', instance_rpid, instance_email, public_dns_name, e
                continue

            netstat_out = ssh_stdout.read()
            ssh_tunnel_up = True
            # print 'OUT', netstat_out
            if ':2046' not in netstat_out:
                ssh_tunnel_up = False
                print 'RPI_SSH_DOWN:', instance_rpid, instance_email, public_dns_name
            # if ':3808' not in netstat_out:
            #     print 'EC2_PROXY_DOWN:', instance_rpid, instance_email, public_dns_name
            # print 'ERR', ssh_stderr.read()

            cmd_to_execute = '''reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable'''
            ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_to_execute)
            if '0x1' not in ssh_stdout.read():
                print 'EC2_PROXY_DOWN:', instance_rpid, instance_email, public_dns_name
                if fix_proxy:
                    cmd_to_execute = '''reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer /t REG_SZ /d socks=127.0.0.1:3808 /f'''
                    ssh.exec_command(cmd_to_execute)
                    cmd_to_execute = '''reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyOverride /t REG_SZ /d localhost;127.0.0.1;169.254.169.254; /f'''
                    ssh.exec_command(cmd_to_execute)
                    cmd_to_execute = '''reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1 /f'''
                    ssh.exec_command(cmd_to_execute)

            if update and ssh_tunnel_up and lead.raspberry_pi.version != settings.RASPBERRY_PI_VERSION:
                cmd_to_execute = '''ssh pi@localhost -p 2046 "curl https://adsrental.com/static/update_pi.sh | bash"'''
                ssh.exec_command(cmd_to_execute)
                lead.raspberry_pi.version = settings.RASPBERRY_PI_VERSION
                lead.raspberry_pi.save()

            ssh.close()
