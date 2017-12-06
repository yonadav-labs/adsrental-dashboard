import datetime

from django.views import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone

from adsrental.models.legacy import Lead
from adsrental.forms import DashboardForm


class DashboardView(View):
    def get_entries(self, user):
        if not user.utm_source:
            return Lead.objects.all().select_related('raspberry_pi')

        return Lead.objects.filter(utm_source=user.utm_source).select_related('raspberry_pi')

    @method_decorator(login_required)
    def get(self, request):
        entries = self.get_entries(request.user)

        return render(request, 'dashboard.html', dict(
            utm_source=request.user.utm_source,
            entries=entries,
            form=DashboardForm(),
        ))

    @method_decorator(login_required)
    def post(self, request):
        form = DashboardForm(request.POST)
        if form.is_valid():
            entries = self.get_entries(request.user)
            if form.cleaned_data['ec2_state']:
                value = form.cleaned_data['ec2_state']
                if value == 'online':
                    entries = entries.filter(raspberry_pi__last_seen__gt=timezone.now() - datetime.timedelta(hours=14))
                if value == 'offline':
                    entries = entries.filter(raspberry_pi__last_seen__lte=timezone.now() - datetime.timedelta(hours=14))
                if value == 'offline_2days':
                    entries = entries.filter(raspberry_pi__last_seen__lte=timezone.now() - datetime.timedelta(hours=14 + 2 * 24))
                if value == 'offline_5days':
                    entries = entries.filter(raspberry_pi__last_seen__lte=timezone.now() - datetime.timedelta(hours=14 + 5 * 24))

            if form.cleaned_data['tunnel_state']:
                value = form.cleaned_data['tunnel_state']
                if value == 'online':
                    entries = entries.filter(raspberry_pi__tunnel_last_tested__gt=timezone.now() - datetime.timedelta(hours=14))
                if value == 'offline':
                    entries = entries.filter(raspberry_pi__tunnel_last_tested__lte=timezone.now() - datetime.timedelta(hours=14))
                if value == 'offline_2days':
                    entries = entries.filter(raspberry_pi__tunnel_last_tested__lte=timezone.now() - datetime.timedelta(hours=14 + 2 * 24))
                if value == 'offline_5days':
                    entries = entries.filter(raspberry_pi__tunnel_last_tested__lte=timezone.now() - datetime.timedelta(hours=14 + 5 * 24))

            if form.cleaned_data['wrong_password']:
                value = form.cleaned_data['wrong_password']
                if value == 'no':
                    entries = entries.filter(wrong_password=False)
                if value == 'yes':
                    entries = entries.filter(wrong_password=True)
                if value == 'yes_2days':
                    entries = entries.filter(wrong_password=True, raspberry_pi__last_seen__lte=timezone.now() - datetime.timedelta(hours=14 + 2 * 24))
                if value == 'yes_5days':
                    entries = entries.filter(wrong_password=True, raspberry_pi__last_seen__lte=timezone.now() - datetime.timedelta(hours=14 + 5 * 24))

            return render(request, 'dashboard.html', dict(
                utm_source=request.user.utm_source,
                entries=entries,
                form=form,
            ))
