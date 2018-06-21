'Views used by RaspberryPi devices'
import os

from django.views import View
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.conf import settings

from adsrental.models.ec2_instance import EC2Instance, SSHConnectException


class StartReverseTunnelView(View):
    'Start reverse tunnel from EC2. Used as a fallback if RaspberryPi cannot created it by itself'
    def get(self, request, rpid):
        'Start reverse tunnel from EC2. Used as a fallback if RaspberryPi cannot created it by itself'
        ec2_instance = EC2Instance.objects.filter(rpid=rpid.strip(), status=EC2Instance.STATUS_RUNNING).first()
        if not ec2_instance:
            return JsonResponse(dict(result=False))

        try:
            ec2_instance.ssh_execute('ssh -N -D 3808 -p 2046 pi@localhost')
        except SSHConnectException:
            return JsonResponse(dict(result=False))
        return JsonResponse(dict(result=True))


class GetNetstatView(View):
    def add_log(self, request, rpid, message):
        ip_address = request.META.get('REMOTE_ADDR')
        now = timezone.localtime(timezone.now())
        log_path = os.path.join(
            settings.RASPBERRY_PI_LOG_PATH,
            rpid,
            '{}.log'.format(now.strftime('%Y%m%d')),
        )
        if not os.path.exists(os.path.dirname(log_path)):
            os.makedirs(os.path.dirname(log_path))
        with open(log_path, 'a') as log_file:
            log_file.write('{ts}: {ip}: {message}\n'.format(
                ts=now.strftime(settings.SYSTEM_DATETIME_FORMAT),
                ip=ip_address,
                message=message,
            ))

    def get(self, request, rpid):
        'Get netstat output from EC2. Used as a fallback if RaspberryPi cannot get it by itself'
        rpid = rpid.strip()
        ec2_instance = EC2Instance.objects.filter(rpid=rpid, status=EC2Instance.STATUS_RUNNING).first()
        if not ec2_instance:
            return HttpResponse('')
        try:
            output = ec2_instance.ssh_execute('netstat -an')
        except SSHConnectException:
            return HttpResponse('', content_type='text/plain')

        result = []
        if ec2_instance.TUNNEL_RE.search(output):
            result.append('SSH tunnel is UP')
        else:
            result.append('SSH tunnel is DOWN')

        if ec2_instance.REVERSE_TUNNEL_RE.search(output):
            result.append('Reverse tunnel is UP')
        else:
            result.append('Reverse tunnel is DOWN')

        if ec2_instance.RDP_RE.search(output):
            result.append('RDP session is active')
        result.append(output)

        return HttpResponse('\n'.join(result), content_type='text/plain')
