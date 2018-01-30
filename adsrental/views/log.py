import os

from django.views import View
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.conf import settings

from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.models.ec2_instance import EC2Instance
from adsrental.utils import BotoResource


class LogView(View):
    LOG_PATH = '/app/log/{rpid}/{date}.log'

    def add_log(self, request, rpid, message):
        ip_address = request.META.get('REMOTE_ADDR')
        now = timezone.now()
        log_path = LogView.LOG_PATH.format(rpid=rpid, date=now.strftime('%Y%m%d'))
        if not os.path.exists(os.path.dirname(log_path)):
            os.makedirs(os.path.dirname(log_path))
        with open(log_path, 'a') as f:
            f.write('{ts}: {ip}: {message}\n'.format(
                ts=now.strftime('%Y-%m-%d %H:%M:%S'),
                ip=ip_address,
                message=message,
            ))

    def get(self, request):
        rpid = request.GET.get('rpid')
        if not rpid:
            return JsonResponse({'result': False, 'reason': 'RPID not found'})

        if 'm' in request.GET:
            message = request.GET.get('m')
            # self.add_log(request, rpid, 'Client >>> {}'.format(message))
            return JsonResponse({'result': True, 'source': 'client'})

        if 'h' in request.GET:
            ec2_instance = EC2Instance.objects.filter(lead__raspberry_pi__rpid=rpid).first()
            if ec2_instance:
                return HttpResponse(ec2_instance.hostname)
            else:
                return HttpResponse('')

        if 'o' in request.GET:
            ip_address = request.META.get('REMOTE_ADDR')
            raspberry_pi = RaspberryPi.objects.filter(rpid=rpid).first()
            raspberry_pi.update_ping()
            if not raspberry_pi.first_seen:
                self.add_log(request, rpid, 'Tested')
            if raspberry_pi.ipaddress != ip_address:
                instance = BotoResource().get_first_rpid_instance(rpid)
                if instance:
                    raspberry_pi.ec2_hostname = instance.public_dns_name
                    raspberry_pi.ipaddress = instance.public_ip_address
                    raspberry_pi.save()

            if raspberry_pi.first_seen:
                self.add_log(request, rpid, 'Tunnel Online')
            else:
                self.add_log(request, rpid, 'Tunnel Tested')

            return JsonResponse({'result': True, 'ip_address': ip_address, 'source': 'tunnel'})

        if 'p' in request.GET:
            ip_address = request.META.get('REMOTE_ADDR')
            raspberry_pi = RaspberryPi.objects.filter(rpid=rpid).first()
            raspberry_pi.update_ping()
            raspberry_pi.save()

            if raspberry_pi.first_seen:
                self.add_log(request, rpid, 'PING')
            else:
                self.add_log(request, rpid, 'PING Tested')

            restart_required = False
            if raspberry_pi.restart_required:
                restart_required = True
                raspberry_pi.restart_required = False
                raspberry_pi.version = settings.RASPBERRY_PI_VERSION
                raspberry_pi.save()

            return JsonResponse({
                'result': True,
                'ip_address': ip_address,
                'source': 'ping',
                'restart': restart_required,
            })

        return JsonResponse({'result': False, 'reason': 'Unknown command'})
