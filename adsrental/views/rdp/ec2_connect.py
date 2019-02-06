from django.views import View
from django.shortcuts import render, redirect
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages

from adsrental.utils import generate_password, BotoResource
from adsrental.models.lead import Lead
from adsrental.models.ec2_instance import EC2Instance, SSHConnectException


class EC2ConnectView(View):
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
        if action == 'restart_rpi':
            raspberry_pi = ec2_instance.get_raspberry_pi()
            if raspberry_pi:
                raspberry_pi.restart_required = True
                raspberry_pi.save()

            messages.success(request, 'RaspberryPi will restart in a couple of minutes.')

    @method_decorator(login_required)
    def get(self, request, rpid, action=None):
        if rpid == 'redirect':
            return redirect('rdp_ec2_connect', rpid=request.GET.get('rpid', ''))
        is_ready = False

        lead = Lead.objects.filter(raspberry_pi__rpid=rpid).first()
        if not lead:
            messages.warning(request, 'This RPID has no assigned lead.')
            return render(request, 'rdp/ec2_connect.html', dict(
                rpid=rpid,
                ec2_instance=None,
                check_connection=False,
                is_ready=is_ready,
                netstat_url='',
            ))
        if lead.raspberry_pi and lead.raspberry_pi.is_proxy_tunnel:
            return redirect('rpi_proxy_tunnel_info', rpid=rpid)

        ec2_instance = EC2Instance.get_by_rpid(rpid)

        if not ec2_instance:
            ec2_instance = EC2Instance.objects.filter(lead=lead).first()
            if ec2_instance:
                ec2_instance.rpid = rpid
                ec2_instance.save()

        if not ec2_instance:
            ec2_instance = EC2Instance.launch_for_lead(lead)
            # ec2_instance = EC2Instance.objects.filter(is_essential=True, rpid__isnull=True, status=EC2Instance.STATUS_RUNNING).first()
            # if not ec2_instance:
            #     ec2_instance = EC2Instance.objects.filter(is_essential=True, rpid__isnull=True).first()

            # stopped_essential_ec2 = EC2Instance.objects.filter(is_essential=True, rpid__isnull=True, status=EC2Instance.STATUS_STOPPED).first()
            # if stopped_essential_ec2:
            #     stopped_essential_ec2.start()
            # else:
            #     # EC2Instance.launch_essential()

            # if not ec2_instance:
            #     ec2_instance = EC2Instance.launch_essential()
            #     messages.info(request, 'New Essential EC2 instance has been launched.')
            #     return redirect('rpi_proxy_tunnel_info', rpid=rpid)
            # ec2_instance.assign_essential(rpid, lead)

        if ec2_instance.is_essential:
            messages.success(request, 'Using essential EC2.')

        raspberry_pi = ec2_instance.get_raspberry_pi()
        if not raspberry_pi or not raspberry_pi.online():
            messages.warning(request, 'Assigned RaspberryPi device is offline, please ping support')

        if ec2_instance.is_stopped() and ec2_instance.instance_type != EC2Instance.INSTANCE_TYPE_M5_LARGE:
            client = BotoResource().get_client('ec2')
            client.modify_instance_attribute(InstanceId=ec2_instance.instance_id, Attribute='instanceType', Value=EC2Instance.INSTANCE_TYPE_M5_LARGE)
            ec2_instance.instance_type = EC2Instance.INSTANCE_TYPE_M5_LARGE
            ec2_instance.save()

        if action:
            self.handle_action(request, ec2_instance, action)
            return redirect('rdp_ec2_connect', rpid=ec2_instance.rpid)
        ec2_instance.update_from_boto()
        if not ec2_instance.is_running():
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
            elif not ec2_instance.REVERSE_TUNNEL_RE.search(netstat_output):
                try:
                    ec2_instance.ssh_execute('ssh -N -D 3808 -p 2046 pi@localhost')
                except SSHConnectException:
                    messages.warning(request, 'Reverse Tunnel is down, instance has no internet connection yet')
                else:
                    messages.info(request, 'Reverse tunnel has been started')

        if ec2_instance.is_running():
            if ec2_instance.password == settings.EC2_ADMIN_PASSWORD:
                try:
                    ec2_instance.change_password(generate_password(length=12))
                except SSHConnectException:
                    pass

        return render(request, 'rdp/ec2_connect.html', dict(
            rpid=rpid,
            ec2_instance=ec2_instance,
            check_connection=True,
            is_ready=is_ready,
            netstat_url=request.build_absolute_uri(reverse('ec2_ssh_get_netstat', kwargs=dict(rpid=rpid))),
        ))
