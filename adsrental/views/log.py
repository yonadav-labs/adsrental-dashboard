import os
import json
from distutils.version import StrictVersion  # pylint: disable=no-name-in-module,import-error

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
from adsrental.utils import PingCacheHelper


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

    def fix_ec2_state(self, request, rpid, lead_status, ec2_instance_status):
        if not Lead.is_status_active(lead_status) and EC2Instance.is_status_running(ec2_instance_status):
            self.add_log(request, rpid, 'Stopping EC2')
            ec2_instance = EC2Instance.get_by_rpid(rpid)
            if ec2_instance and not ec2_instance.is_essential:
                ec2_instance.stop()
            return True

        return False

    def get_old_client_log_handler(self, request, rpid):
        message = request.GET.get('m')
        self.add_log(request, rpid, 'Old Client >>> {}'.format(message))
        return JsonResponse({'result': True, 'source': 'client'})

    def get_client_log_hadler(self, request, rpid):
        message = request.GET.get('client_log')
        self.add_log(request, rpid, 'Client >>> {}'.format(message))
        return JsonResponse({'result': True, 'source': 'client'})

    def get_hostname_hadler(self, request, rpid):
        ping_cache_helper = PingCacheHelper()
        ping_data = ping_cache_helper.get_data_for_request(request)
        return HttpResponse(ping_data.get('ec2_hostname') or '')

    def _get_restart_required(self, ping_data):
        version = ping_data.get('raspberry_pi_version')
        restart_required = ping_data.get('restart_required')
        if version and StrictVersion(version) < StrictVersion('1.1.2'):
            return True

        if restart_required:
            return True

        return False

    def _get_update_required(self, ping_data):
        version = ping_data.get('raspberry_pi_version')
        if not version:
            return False

        if version != settings.RASPBERRY_PI_VERSION:
            return True

        if ping_data.get('is_beta') and StrictVersion(version) < StrictVersion(settings.BETA_RASPBERRY_PI_VERSION):
            return True

        return False

    def _get_new_config_required(self, ping_data):
        reported_hostname = ping_data.get('reported_hostname')
        ec2_hostname = ping_data.get('ec2_hostname')
        ec2_ip_address = ping_data.get('ec2_ip_address')
        new_config_required = ping_data.get('new_config_required')

        if new_config_required:
            return True

        if reported_hostname is not None and ec2_hostname:
            if reported_hostname not in (ec2_hostname, ec2_ip_address):
                return True

        return False

    def get_ping_handler(self, request, rpid):
        ping_cache_helper = PingCacheHelper()
        ping_data = ping_cache_helper.get_data_for_request(request)
        ping_data['last_ping'] = timezone.now()
        ping_cache_helper.set(rpid, ping_data)

        self.fix_ec2_state(request, rpid, lead_status=ping_data['lead_status'], ec2_instance_status=ping_data['ec2_instance_status'])

        self.add_log(request, rpid, 'PING {}'.format(request.GET.urlencode()))

        response_data = self._get_ping_response_data(request, rpid, ping_data)
        return self.json_response(request, rpid, response_data)

    def _get_ping_response_data(self, request, rpid, ping_data):
        lead_status = ping_data['lead_status']
        wrong_password = ping_data.get('wrong_password')

        reason = None
        result = True

        if not Lead.is_status_active(lead_status):
            reason = 'Lead not found or banned'
            response_data = {
                'reason': reason,
                'source': 'ping',
                'result': result,
            }
            return response_data

        if wrong_password:
            reason = 'Wrong password'
            result = False

        response_data = {
            'source': 'ping',
            'result': result,
        }

        restart_required = self._get_restart_required(ping_data)
        new_config_required = self._get_new_config_required(ping_data)
        update_required = self._get_update_required(ping_data)

        if new_config_required:
            self.add_log(request, rpid, 'Sending info about config update')
            response_data['new_config'] = new_config_required

        if restart_required:
            self.add_log(request, rpid, 'Restarting RaspberryPi')
            response_data['restart'] = restart_required

        if update_required:
            self.add_log(request, rpid, 'RaspberryPi image updated, updating...')
            response_data['update'] = update_required

        return response_data

    def get(self, request):
        rpid = request.GET.get('rpid', '').strip()
        if not rpid:
            return JsonResponse({'result': False, 'reason': 'RPID not found'})

        if 'm' in request.GET:
            return self.get_old_client_log_handler(request, rpid)

        if 'client_log' in request.GET:
            return self.get_client_log_hadler(request, rpid)

        if 'h' in request.GET:
            return self.get_hostname_hadler(request, rpid)

        if 'p' in request.GET:
            return self.get_ping_handler(request, rpid)

        return JsonResponse({'result': False, 'reason': 'Unknown command'})

    def json_response(self, request, rpid, data):
        self.add_log(request, rpid, 'Response: {}'.format(json.dumps(data)))
        return JsonResponse(data)
