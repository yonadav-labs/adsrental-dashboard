import re

import requests
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.contrib import messages
from django.conf import settings

from adsrental.models.raspberry_pi import RaspberryPi


class ProxyTunnelInfoView(View):
    @method_decorator(login_required)
    def get(self, request, rpid):
        now = timezone.localtime(timezone.now())
        raspberry_pi = RaspberryPi.objects.get(rpid=rpid)
        if not raspberry_pi.is_proxy_tunnel:
            messages.warning(request, 'This device cannot be used as a proxy tunnel. Use "Make proxy tunnel" action.')
        if not raspberry_pi.online():
            messages.warning(request, 'This device is currently offline.')
        
        last_log = raspberry_pi.get_last_log(tail=500)
        unique_ips_count = len(list(set(re.findall(r'\d+\.\d+\.\d+\.\d+', last_log))))
        if unique_ips_count > 9:
            messages.warning(request, f'This device is changing IP addresses to often, connection can be unstable. {unique_ips_count} IP changes detected.')

        try:
            test_tunnel_response = requests.get(
                'http://ya.ru',
                proxies=dict(
                    http=f'socks5://{raspberry_pi.TUNNEL_USER}:{raspberry_pi.TUNNEL_PASSWORD}@{raspberry_pi.proxy_hostname}:{raspberry_pi.rtunnel_port}',
                ),
                timeout=5,
            ).ok
        except requests.ConnectionError:
            test_tunnel_response = False
        if test_tunnel_response:
            messages.success(request, 'Proxy tunnel is working correctly.')
        else:
            messages.error(request, 'Proxy tunnel is not working correctly.')


        return render(request, 'rpi/proxy_tunnel_info.html', dict(
            user=request.user,
            raspberry_pi=raspberry_pi,
            lead=raspberry_pi.get_lead(),
            is_online=raspberry_pi.online(),
            today_log_filename='{}.log'.format(now.strftime(settings.LOG_DATE_FORMAT)),
        ))

    @method_decorator(login_required)
    def post(self, request, rpid):
        raspberry_pi = RaspberryPi.objects.get(rpid=rpid)
        action = request.POST.get('action')
        if action == 'new_config':
            raspberry_pi.reset_cache()
            raspberry_pi.new_config_required = True
            raspberry_pi.save()
            messages.success(request, 'New config successfully requested. Tunnel should be online in two minutes.')
        if action == 'restart':
            raspberry_pi.reset_cache()
            raspberry_pi.restart_required = True
            raspberry_pi.save()
            messages.success(request, 'Restart successfully requested. RPi and tunnel should be online in two minutes.')
        if action == 'make_proxy_tunnel':
            raspberry_pi.reset_cache()
            raspberry_pi.is_proxy_tunnel = True
            raspberry_pi.new_config_required = True
            raspberry_pi.assign_proxy_hostname()
            raspberry_pi.assign_tunnel_ports()
            raspberry_pi.save()

            ec2_instance = raspberry_pi.get_ec2_instance()
            if ec2_instance:
                ec2_instance.unassign_essential()
                ec2_instance.stop()
                messages.info(request, 'Unassigned EC2.')
            messages.success(request, 'Device can be used as a proxy tunnel in a couple of minutes!')

        return redirect('rpi_proxy_tunnel_info', rpid=raspberry_pi.rpid)
