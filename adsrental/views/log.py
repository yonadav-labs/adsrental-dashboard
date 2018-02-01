import os
import json

from django.views import View
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.conf import settings

from adsrental.models.lead import Lead
from adsrental.models.ec2_instance import EC2Instance


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
            return JsonResponse({'result': True, 'source': 'client'})

        if 'client_log' in request.GET:
            message = request.GET.get('client_log')
            self.add_log(request, rpid, 'Client >>> {}'.format(message))
            return JsonResponse({'result': True, 'source': 'client'})

        if 'h' in request.GET:
            ec2_instance = EC2Instance.objects.filter(lead__raspberry_pi__rpid=rpid).first()
            if ec2_instance:
                return HttpResponse(ec2_instance.hostname)
            else:
                return HttpResponse('')

        if 'o' in request.GET:
            ip_address = request.META.get('REMOTE_ADDR')
            lead = Lead.objects.filter(raspberry_pi__rpid=rpid).first()
            if not lead:
                return self.json_response(request, rpid, {
                    'result': False,
                    'reason': 'Lead not found',
                    'rpid': rpid,
                    'source': 'tunnel',
                })

            raspberry_pi = lead.raspberry_pi
            ec2_instance = lead.get_ec2_instance()

            raspberry_pi.update_ping()
            if not raspberry_pi.first_seen:
                self.add_log(request, rpid, 'Tested')

            if raspberry_pi.first_seen:
                self.add_log(request, rpid, 'Tunnel Online')
            else:
                self.add_log(request, rpid, 'Tunnel Tested')

            if ec2_instance.ip_address != ip_address:
                self.add_log(request, rpid, 'Updating EC2 IP address to {}'.format(ip_address))
                ec2_instance.update_from_boto()

            return self.json_response(request, rpid, {'result': True, 'ip_address': ip_address, 'source': 'tunnel'})

        if 'p' in request.GET:
            ip_address = request.META.get('REMOTE_ADDR')
            hostname = request.GET.get('hostname')
            version = request.GET.get('version')
            lead = Lead.objects.filter(raspberry_pi__rpid=rpid).first()
            if not lead:
                return self.json_response(request, rpid, {
                    'result': False,
                    'reason': 'Lead not found',
                    'rpid': rpid,
                    'source': 'ping',
                })

            raspberry_pi = lead.raspberry_pi
            ec2_instance = lead.get_ec2_instance()
            raspberry_pi.update_ping()
            raspberry_pi.save()

            if raspberry_pi.first_seen:
                self.add_log(request, rpid, 'PING {} for {}'.format(version, hostname))
            else:
                self.add_log(request, rpid, 'PING Test {} for {}'.format(version, hostname))

            if not version and ec2_instance and ec2_instance.tunnel_up:
                self.add_log(request, rpid, 'Trying to force update old version')
                cmd_to_execute = '''ssh pi@localhost -p 2046 "curl https://adsrental.com/static/update_pi.sh | bash"'''
                try:
                    ssh = ec2_instance.get_ssh()
                    ssh.exec_command(cmd_to_execute)
                except:
                    self.add_log(request, rpid, 'Update failed, tunnel is down')

            if version and raspberry_pi.version != version:
                self.add_log(request, rpid, 'RaspberryPI updated to {}'.format(version))
                raspberry_pi.version = version
                raspberry_pi.save()

            restart_required = False
            if version and settings.RASPBERRY_PI_VERSION > version:
                self.add_log(request, rpid, 'RaspberryPi image updated, restarting')
                restart_required = True

            if hostname and ec2_instance.hostname != hostname:
                self.add_log(request, rpid, 'Hostname changed, restarting')
                restart_required = True

            if raspberry_pi.restart_required:
                self.add_log(request, rpid, 'Restarting RaspberryPi on demand')
                restart_required = True
                raspberry_pi.restart_required = False
                raspberry_pi.save()

            return self.json_response(request, rpid, {
                'result': True,
                'ip_address': ip_address,
                'source': 'ping',
                'restart': restart_required,
            })

        return JsonResponse({'result': False, 'reason': 'Unknown command'})

    def json_response(self, request, rpid, data):
        self.add_log(request, rpid, 'Response: {}'.format(json.dumps(data)))
        return JsonResponse(data)
