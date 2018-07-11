'Views used by RaspberryPi devices'
import os
import time

from django.views import View
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.conf import settings

from adsrental.models.ec2_instance import EC2Instance, SSHConnectException


class StartReverseTunnelView(View):
    'Start reverse tunnel from EC2. Used as a fallback if RaspberryPi cannot created it by itself'
    MAX_ATTEMPTS = 10
    def get(self, request, rpid):
        'Start reverse tunnel from EC2. Used as a fallback if RaspberryPi cannot created it by itself'
        ec2_instance = EC2Instance.get_by_rpid(rpid)
        if not ec2_instance or not ec2_instance.is_running():
            return JsonResponse(dict(result=False))

        tunnel_up = False
        attempts = 0
        netstat_output = True

        while not tunnel_up and attempts < self.MAX_ATTEMPTS and netstat_output:
            attempts += 1
            netstat_output = ''
            try:
                netstat_output = ec2_instance.ssh_execute('netstat -an') or ''
            except SSHConnectException:
                pass

            if ec2_instance.REVERSE_TUNNEL_RE.search(netstat_output):
                tunnel_up = True
                break

            try:
                ec2_instance.ssh_execute('ssh -N -D 3808 -p 2046 pi@localhost')
            except SSHConnectException:
                pass
            time.sleep(5)

        return JsonResponse(dict(
            result=tunnel_up,
            attempts=attempts,
            netstat=ec2_instance.REVERSE_TUNNEL_RE.search(netstat_output),
        ))


class GetNetstatView(View):
    def get(self, request, rpid):
        'Get netstat output from EC2. Used as a fallback if RaspberryPi cannot get it by itself'
        rpid = rpid.strip()
        ec2_instance = EC2Instance.get_by_rpid(rpid)
        if not ec2_instance or not ec2_instance.is_running():
            return HttpResponse('Not exists')
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
