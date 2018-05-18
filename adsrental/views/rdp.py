from __future__ import unicode_literals

from django.views import View
from django.http import FileResponse, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages

from adsrental.utils import generate_password
from adsrental.models.raspberry_pi import RaspberryPi
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
        if action == 'update_antidetect':
            try:
                ec2_instance.ssh_execute('powershell iwr https://adsrental.com/static/browser.exe -outf C:\\Users\\Administrator\\Desktop\\Browser.exe')
            except SSHConnectException:
                messages.warning(request, 'Antidetect script update failed.')
                return
            messages.success(request, 'Antidetect script updated successfully')
        if action == 'fix_performance':
            try:
                ec2_instance.ssh_execute('reg add "HKEY_LOCAL_MACHINE\\SOFTWARE\\Policies\\Microsoft\\Windows Defender" /v DisableAntiSpyware /t REG_DWORD /d 1 /f')
            except SSHConnectException:
                messages.warning(request, 'Performance fixed failed.')
                return
            messages.success(request, 'Performance fixed applied successfully, instance is rebooting.')
            ec2_instance.stop()

    @method_decorator(login_required)
    def get(self, request):
        rpid = request.GET.get('rpid', 'none')
        force = request.GET.get('force', '') == 'true'
        action = request.GET.get('action', '')
        is_ready = False
        ec2_instance = EC2Instance.objects.filter(rpid=rpid).first()
        if ec2_instance:
            if action:
                self.handle_action(request, ec2_instance, action)
            ec2_instance.update_from_boto()
            if not ec2_instance.is_running() or force:
                ec2_instance.last_rdp_start = timezone.now()
                ec2_instance.save()
                ec2_instance.start()

            try:
                ec2_instance.ssh_execute('netstat -an')
            except SSHConnectException:
                pass
            else:
                is_ready = True

            if ec2_instance.is_running():
                if ec2_instance.password == settings.EC2_ADMIN_PASSWORD:
                    try:
                        ec2_instance.change_password(generate_password(length=12))
                    except SSHConnectException:
                        pass


        return render(request, 'rdp_connect.html', dict(
            rpid=rpid,
            ec2_instance=ec2_instance,
            is_ready=is_ready,
            netstat_url=request.build_absolute_uri(reverse('ec2_ssh_get_netstat', kwargs=dict(rpid=rpid))),
        ))
