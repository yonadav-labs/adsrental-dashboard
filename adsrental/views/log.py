from __future__ import unicode_literals

import os
import json
from distutils.version import StrictVersion

from django.views import View
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import Http404

from adsrental.models.lead import Lead
from adsrental.models.ec2_instance import EC2Instance


class ShowLogDirView(View):
    @method_decorator(login_required)
    def get(self, request, rpid):
        path = os.path.join(settings.RASPBERRY_PI_LOG_PATH, rpid)
        if not os.path.exists(path):
            raise Http404
        filenames = os.listdir(path)
        filenames.sort(reverse=True)
        return render(request, 'log_dir.html', dict(
            user=request.user,
            rpid=rpid,
            filenames=filenames,
        ))


class ShowLogView(View):
    @method_decorator(login_required)
    def get(self, request, rpid, filename):
        log_path = os.path.join(settings.RASPBERRY_PI_LOG_PATH, rpid, filename)
        if not os.path.exists(log_path):
            raise Http404
        return HttpResponse(open(log_path).read(), content_type='text/plain')


class LogView(View):
    def add_log(self, request, rpid, message):
        ip_address = request.META.get('REMOTE_ADDR')
        now = timezone.now()
        log_path = os.path.join(
            settings.RASPBERRY_PI_LOG_PATH,
            rpid,
            '{}.log'.format(now.strftime('%Y%m%d')),
        )
        if not os.path.exists(os.path.dirname(log_path)):
            os.makedirs(os.path.dirname(log_path))
        with open(log_path, 'a') as f:
            f.write('{ts}: {ip}: {message}\n'.format(
                ts=now.strftime(settings.SYSTEM_DATETIME_FORMAT),
                ip=ip_address,
                message=message,
            ))

    def get(self, request):
        rpid = request.GET.get('rpid')
        if not rpid:
            return JsonResponse({'result': False, 'reason': 'RPID not found'})

        if 'm' in request.GET:
            message = request.GET.get('m')
            self.add_log(request, rpid, 'Old Client >>> {}'.format(message))
            return JsonResponse({'result': True, 'source': 'client'})

        if 'client_log' in request.GET:
            message = request.GET.get('client_log')
            self.add_log(request, rpid, 'Client >>> {}'.format(message))
            return JsonResponse({'result': True, 'source': 'client'})

        if 'h' in request.GET:
            ec2_instance = EC2Instance.objects.filter(lead__raspberry_pi__rpid=rpid).select_related('lead').first()
            if not ec2_instance:
                return HttpResponse('')
            if not ec2_instance.lead:
                return HttpResponse('')
            if not ec2_instance.lead.is_active():
                if not ec2_instance.is_stopped():
                    ec2_instance.stop()
                return HttpResponse('')

            if not ec2_instance.is_running():
                ec2_instance.start()
                if not ec2_instance.is_running():
                    return HttpResponse('')

            ec2_instance.tunnel_up = False
            ec2_instance.save()
            return HttpResponse(ec2_instance.hostname)

        if 'o' in request.GET:
            return JsonResponse({'result': True})
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

            # if ec2_instance.ip_address != ip_address:
            #     self.add_log(request, rpid, 'Updating EC2 IP address to {}'.format(ip_address))
            #     ec2_instance.update_from_boto()

            return self.json_response(request, rpid, {'result': True, 'ip_address': ip_address, 'source': 'tunnel'})

        if 'p' in request.GET:
            ip_address = request.META.get('REMOTE_ADDR')
            hostname = request.GET.get('hostname')
            version = request.GET.get('version')
            troubleshoot = request.GET.get('troubleshoot')
            lead = Lead.objects.filter(raspberry_pi__rpid=rpid).select_related('ec2instance', 'raspberry_pi').first()
            if not lead or not lead.is_active():
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

            if lead.is_active() and ec2_instance and not ec2_instance.is_running():
                self.add_log(request, rpid, 'EC2 is now {}, trying to start'.format(ec2_instance.status))
                ec2_instance.start()

            self.add_log(request, rpid, 'PING {}'.format(request.GET.urlencode()))

            restart_required = False
            new_config_required = False
            update_required = False

            if troubleshoot and ec2_instance:
                main_tunnel_up = request.GET.get('tunnel_up', '0') == '1'
                reverse_tunnel_up = request.GET.get('reverse_tunnel_up', '1') == '1'
                tunnel_up = main_tunnel_up and reverse_tunnel_up
                if tunnel_up:
                    ec2_instance.tunnel_up_date = timezone.now()
                ec2_instance.tunnel_up = tunnel_up
                ec2_instance.last_troubleshoot = timezone.now()
                ec2_instance.save()

                # if not main_tunnel_up:
                #     self.add_log(request, rpid, 'Tunnel seems to be down')
                #     # restart_required = True
                # if not reverse_tunnel_up:
                #     self.add_log(request, rpid, 'Reverse tunnel seems to be down')
                #     # restart_required = True

                # if not ec2_instance.tunnel_up_date or ec2_instance.tunnel_up_date < timezone.now() - datetime.timedelta(minutes=30):
                #     self.add_log(request, rpid, 'TUnnel is down for more than 30 minutes, getting new config')
                #     new_config_required = True

            if version and raspberry_pi.version != version:
                self.add_log(request, rpid, 'RaspberryPI updated to {}'.format(version))
                raspberry_pi.version = version
                raspberry_pi.save()

            if version and settings.RASPBERRY_PI_VERSION != version and StrictVersion(settings.RASPBERRY_PI_VERSION) > StrictVersion(version):
                self.add_log(request, rpid, 'RaspberryPi image updated, updating...')
                update_required = True
                if version and StrictVersion(version) < StrictVersion('1.1.2'):
                    restart_required = True

            if hostname is not None and ec2_instance.is_running():
                if ec2_instance.hostname != hostname and ec2_instance.ip_address != hostname:
                    self.add_log(request, rpid, 'Hostname changed, restarting')
                    new_config_required = True
                    if version and StrictVersion(version) < StrictVersion('1.1.2'):
                        restart_required = True

            if raspberry_pi.restart_required:
                self.add_log(request, rpid, 'Restarting RaspberryPi on demand')
                restart_required = True
                raspberry_pi.restart_required = False
                raspberry_pi.save()

            response_data = {
                'result': True,
                'source': 'ping',
            }
            if restart_required:
                response_data['restart'] = restart_required
            if new_config_required:
                response_data['new_config'] = new_config_required
            if update_required:
                response_data['update'] = update_required

            return self.json_response(request, rpid, response_data)

        return JsonResponse({'result': False, 'reason': 'Unknown command'})

    def json_response(self, request, rpid, data):
        self.add_log(request, rpid, 'Response: {}'.format(json.dumps(data)))
        return JsonResponse(data)
