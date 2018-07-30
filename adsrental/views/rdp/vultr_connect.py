from django.views import View
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, Http404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from adsrental.models.vultr_instance import VultrInstance


class VultrConnectView(View):
    def handle_action(self, request, vultr_instance, action):
        if action == 'refresh':
            vultr_instance.update_from_vultr()
            messages.success(request, 'Instance state updated.')

    @method_decorator(login_required)
    def get(self, request, vultr_instance_id, action=None):
        vultr_instance = get_object_or_404(VultrInstance, id=vultr_instance_id)

        if action:
            self.handle_action(request, vultr_instance, action)
            return redirect('rdp_vultr_connect', vultr_instance_id=vultr_instance.id)

        if not vultr_instance.is_running():
            raise Http404
        return render(request, 'rdp/vultr_connect.html', dict(
            vultr_instance=vultr_instance,
        ))
