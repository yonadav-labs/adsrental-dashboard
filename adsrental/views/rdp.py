from __future__ import unicode_literals

from django.views import View
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages

from adsrental.utils import generate_password, BotoResource
from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.models.lead import Lead
from adsrental.models.ec2_instance import EC2Instance, SSHConnectException


class RDPDownloadView(View):
    @method_decorator(login_required)
    def get(self, request, rpid):
        raspberry_pi = RaspberryPi.objects.filter(rpid=rpid).first()
        ec2_instance = raspberry_pi.get_ec2_instance()

        if not ec2_instance:
            return HttpResponse('EC2 instance {} does not exist'.format(rpid))

        lines = []
        lines.append('auto connect:i:1')
        lines.append('full address:s:{}:23255'.format(ec2_instance.hostname))
        lines.append('username:s:Administrator')
        lines.append('password:s:{}'.format(ec2_instance.password))
        lines.append('')
        content = '\n'.join(lines)

        response = FileResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="{}.rdp"'.format(rpid)
        return response


class RDPConnectView(View):
    def handle_action(self, request, ec2_instance, action):
        if action == 'install_antidetect_script':
            try:
                ec2_instance.ssh_execute('powershell iwr https://adsrental.com/static/antidetect/install_antidetect.bat -outf C:\\install_antidetect.bat')
                ec2_instance.ssh_execute('start "" C:\\install_antidetect.bat')
            except SSHConnectException:
                messages.warning(request, 'Antidetect script update failed.')
                return
            messages.success(request, 'Antidetect script updated successfully. Shortcut on desktop Should appear in 5 minutes max.')
            ec2_instance.browser_type = ec2_instance.BROWSER_TYPE_ANTIDETECT_7_3_3
            ec2_instance.save()
        if action == 'install_mla_script':
            try:
                ec2_instance.ssh_execute('powershell iwr https://adsrental.com/static/mla/install_mla.bat -outf C:\\install_mla.bat')
                ec2_instance.ssh_execute('start "" C:\\install_mla.bat')
            except SSHConnectException:
                messages.warning(request, 'MLA script update failed.')
                return

            ec2_instance.browser_type = ec2_instance.BROWSER_TYPE_MLA
            ec2_instance.save()
            messages.success(request, 'MLA script updated successfully. Shortcut on desktop Should appear in 5 minutes max.')
        if action == 'fix_performance':
            try:
                ec2_instance.ssh_execute('reg add "HKEY_LOCAL_MACHINE\\SOFTWARE\\Policies\\Microsoft\\Windows Defender" /v DisableAntiSpyware /t REG_DWORD /d 1 /f')
            except SSHConnectException:
                messages.warning(request, 'Performance fixed failed.')
                return
            messages.success(request, 'Performance fixed applied successfully, instance is rebooting.')
        if action == 'enable_proxy':
            ec2_instance.enable_proxy()
            messages.success(request, 'Proxy is successfully enabled')
        if action == 'disable_proxy':
            ec2_instance.disable_proxy()
            messages.success(request, 'Proxy is successfully disabled')

    @method_decorator(login_required)
    def get(self, request):
        rpid = request.GET.get('rpid', 'none')
        force = request.GET.get('force', '') == 'true'
        action = request.GET.get('action', '')
        is_ready = False

        lead = Lead.objects.filter(raspberry_pi__rpid=rpid).first()
        if not lead:
            messages.warning(request, 'This RPID has no assigned lead.')
            return render(request, 'rdp_connect.html', dict(
                rpid=rpid,
                ec2_instance=None,
                check_connection=False,
                is_ready=is_ready,
                netstat_url=request.build_absolute_uri(reverse('ec2_ssh_get_netstat', kwargs=dict(rpid=rpid))),
            ))

        ec2_instance = EC2Instance.get_by_rpid(rpid)
        if not ec2_instance:
            ec2_instance = EC2Instance.objects.filter(is_essential=True, rpid__isnull=True).first()
            if not ec2_instance:
                ec2_instance = EC2Instance.launch_essential()
                messages.info(request, 'New Essential EC2 instance has been launched.')
            ec2_instance.assign_essential(rpid, lead)

        if ec2_instance.is_essential:
            messages.success(request, 'Using essential EC2.')

        raspberry_pi = ec2_instance.get_raspberry_pi()
        if not raspberry_pi or not raspberry_pi.online():
            messages.warning(request, 'Assigned RaspberryPi device is offline, please ping support')

        if ec2_instance.is_stopped() and ec2_instance.instance_type != EC2Instance.INSTANCE_TYPE_M5_LARGE:
            client = BotoResource().get_client('ec2')
            try:
                client.modify_instance_attribute(InstanceId=ec2_instance.instance_id, Attribute='instanceType', Value=EC2Instance.INSTANCE_TYPE_M5_LARGE)
                ec2_instance.instance_type = EC2Instance.INSTANCE_TYPE_M5_LARGE
                ec2_instance.save()
            except Exception:
                pass

        if action:
            self.handle_action(request, ec2_instance, action)
            return HttpResponseRedirect('{}?rpid={}'.format(reverse('rdp_connect'), ec2_instance.rpid))
        ec2_instance.update_from_boto()
        if not ec2_instance.is_running() or force:
            ec2_instance.start()

        ec2_instance.last_rdp_start = timezone.now()
        ec2_instance.save()

        netstat_output = ''
        try:
            netstat_output = ec2_instance.ssh_execute('netstat -an', timeout=5)
        except SSHConnectException:
            messages.warning(request, 'SSH is down, instance is not usable now')
        else:
            is_ready = True
            if not ec2_instance.TUNNEL_RE.search(netstat_output):
                messages.warning(request, 'SSH Tunnel is down, instance has no internet connection yet')
            if not ec2_instance.REVERSE_TUNNEL_RE.search(netstat_output):
                messages.warning(request, 'Reverse Tunnel is down, instance has no internet connection yet')

        if ec2_instance.is_running():
            if ec2_instance.password == settings.EC2_ADMIN_PASSWORD:
                try:
                    ec2_instance.change_password(generate_password(length=12))
                except SSHConnectException:
                    pass

        return render(request, 'rdp_connect.html', dict(
            rpid=rpid,
            ec2_instance=ec2_instance,
            check_connection=True,
            is_ready=is_ready,
            netstat_url=request.build_absolute_uri(reverse('ec2_ssh_get_netstat', kwargs=dict(rpid=rpid))),
        ))
