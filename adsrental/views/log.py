from __future__ import unicode_literals

import os
import json
from distutils.version import StrictVersion

from django.core.cache import cache
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
from adsrental.models.raspberry_pi import RaspberryPi


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
    PING_DATA_TTL_SECONDS = 300

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

    def get_actual_ping_data(self, request):
        rpid = request.GET.get('rpid')
        ip_address = request.META.get('REMOTE_ADDR')
        version = request.GET.get('version')
        lead = Lead.objects.filter(raspberry_pi__rpid=rpid).select_related('ec2instance', 'raspberry_pi').first()
        raspberry_pi = lead and lead.raspberry_pi
        ec2_instance = lead and lead.get_ec2_instance()
        ping_data = {
            'rpid': rpid,
            'lead_status': lead and lead.status,
            'raspberry_pi_version': version,
            'restart_required': raspberry_pi and raspberry_pi.restart_required,
            'ec2_instance_id': ec2_instance and ec2_instance.instance_id,
            'ec2_instance_status': ec2_instance and ec2_instance.status,
            'ec2_hostname': ec2_instance and lead.is_active() and ec2_instance.is_running() and ec2_instance.hostname,
            'ec2_ip_address': ec2_instance and ec2_instance.ip_address,
            'ip_address': ip_address,
        }
        return ping_data

    def get_ping_data(self, request, update_ping=False, refresh=False):
        rpid = request.GET.get('rpid')
        troubleshoot = request.GET.get('troubleshoot')
        main_tunnel_up = request.GET.get('tunnel_up', '0') == '1'
        reverse_tunnel_up = request.GET.get('reverse_tunnel_up', '1') == '1'
        now = timezone.now()

        ping_key = RaspberryPi.get_ping_key(rpid)
        ping_data = None
        if not refresh:
            ping_data = cache.get(ping_key)
        if not ping_data:
            ping_data = self.get_actual_ping_data(request)
        else:
            if ping_data.get('restart_required'):
                ping_data['restart_required'] = False

        if update_ping:
            ping_data['last_ping'] = now

        if troubleshoot:
            tunnel_up = main_tunnel_up and reverse_tunnel_up
            ping_data['tunnel_up'] = tunnel_up
            ping_data['last_troubleshoot'] = now

        cache.set(ping_key, ping_data, self.PING_DATA_TTL_SECONDS)
        ping_keys = cache.get('ping_keys', [])
        if ping_key not in ping_keys:
            ping_keys.append(ping_key)
            cache.set('ping_keys', ping_keys)

        if 'lead_status' not in ping_data:
            raise ValueError(ping_data)
        if self.fix_ec2_state(request, rpid, lead_status=ping_data['lead_status'], ec2_instance_status=ping_data['ec2_instance_status']):
            cache.delete(ping_key)

        return ping_data

    def fix_ec2_state(self, request, rpid, lead_status, ec2_instance_status):
        if Lead.is_status_active(lead_status):
            if not EC2Instance.is_status_active(ec2_instance_status):
                ec2_instance = EC2Instance.objects.filter(rpid=rpid).first()
                if not ec2_instance:
                    self.add_log(request, rpid, 'Trying to launch missing EC2')
                    lead = Lead.objects.filter(raspberry_pi__rpid=rpid).first()
                    EC2Instance.launch_for_lead(lead)
                    return True
                self.add_log(request, rpid, 'Starting stopped EC2')
                ec2_instance.start()
                return True
        if not Lead.is_status_active(lead_status) and EC2Instance.is_status_running(ec2_instance_status):
            self.add_log(request, rpid, 'Stopping EC2')
            ec2_instance = EC2Instance.objects.filter(rpid=rpid).first()
            ec2_instance.stop()
            return True

        return False

    def get(self, request):
        rpid = request.GET.get('rpid', '').strip()
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
            ping_data = self.get_ping_data(request, update_ping=False)
            return HttpResponse(ping_data.get('ec2_hostname') or '')

        if 'p' in request.GET:
            hostname = request.GET.get('hostname')
            ping_data = self.get_ping_data(request, update_ping=True)
            lead_status = ping_data['lead_status']
            ec2_instance_id = ping_data['ec2_instance_id']
            ec2_hostname = ping_data['ec2_hostname']
            ec2_ip_address = ping_data['ec2_ip_address']
            version = ping_data['raspberry_pi_version']
            raspberry_pi_restart_required = ping_data['restart_required']

            if not Lead.is_status_active(lead_status):
                return self.json_response(request, rpid, {
                    'result': False,
                    'reason': 'Lead not found',
                    'rpid': rpid,
                    'source': 'ping',
                })

            if not ec2_instance_id:
                lead = Lead.objects.filter(raspberry_pi__rpid=rpid).first()
                EC2Instance.launch_for_lead(lead)
                self.add_log(request, rpid, 'Trying to launch missing EC2')
                return self.json_response(request, rpid, {'result': True, 'source': 'ping', 'message': 'Launch missing EC2'})

            self.add_log(request, rpid, 'PING {}'.format(request.GET.urlencode()))

            restart_required = False
            new_config_required = False
            update_required = False

            if version and settings.RASPBERRY_PI_VERSION != version and StrictVersion(settings.RASPBERRY_PI_VERSION) > StrictVersion(version):
                self.add_log(request, rpid, 'RaspberryPi image updated, updating...')
                update_required = True
                if version and StrictVersion(version) < StrictVersion('1.1.2'):
                    restart_required = True

            if hostname is not None:
                if ec2_hostname != hostname and ec2_ip_address != hostname:
                    self.add_log(request, rpid, 'Hostname changed, restarting')
                    new_config_required = True
                    if version and StrictVersion(version) < StrictVersion('1.1.2'):
                        restart_required = True

            if raspberry_pi_restart_required:
                self.add_log(request, rpid, 'Restarting RaspberryPi on demand')
                restart_required = True

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
