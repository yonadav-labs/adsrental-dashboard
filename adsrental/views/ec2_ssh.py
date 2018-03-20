'Views used by RaspberryPi devices'
from django.views import View
from django.http import JsonResponse, HttpResponse

from adsrental.models.ec2_instance import EC2Instance, SSHConnectException


class StartReverseTunnelView(View):
    'Start reverse tunnel from EC2. Used as a fallback if RaspberryPi cannot created it by itself'
    def get(self, request, rpid):
        'Start reverse tunnel from EC2. Used as a fallback if RaspberryPi cannot created it by itself'
        ec2_instance = EC2Instance.objects.filter(rpid=rpid.strip()).first()
        if not ec2_instance or not ec2_instance.is_running():
            return JsonResponse(dict(result=False))

        try:
            ec2_instance.ssh_execute('ssh -N -D 3808 -p 2046 pi@localhost')
        except SSHConnectException:
            # ec2_instance.stop()
            return JsonResponse(dict(result=False))
        return JsonResponse(dict(result=True))


class GetNetstatView(View):
    'Get netstat output from EC2. Used as a fallback if RaspberryPi cannot get it by itself'
    def get(self, request, rpid):
        'Get netstat output from EC2. Used as a fallback if RaspberryPi cannot get it by itself'
        ec2_instance = EC2Instance.objects.filter(rpid=rpid.strip()).first()
        if not ec2_instance or not ec2_instance.is_running():
            return HttpResponse('')

        try:
            output = ec2_instance.ssh_execute('netstat -an')
        except SSHConnectException:
            ec2_instance.stop()
            return HttpResponse('', content_type='text/plain')

        return HttpResponse(output, content_type='text/plain')
