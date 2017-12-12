import datetime

from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone

from adsrental.models import Lead
from adsrental.forms import DashboardForm


class CheckSentView(View):
    @method_decorator(login_required)
    def post(self, request):
        lead_id = request.POST.get('leadid')
        lead = Lead.objects.get(leadid=lead_id)
        lead.pi_sent = timezone.now()
        lead.save()
        return redirect('dashboard')


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
            entries=entries.order_by('-raspberry_pi__last_seen')[:100],
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
                    entries = entries.filter(raspberry_pi__last_seen__gt=timezone.now() - datetime.timedelta(hours=14), pi_delivered=True).exclude(status='Banned')
                if value == 'offline':
                    entries = entries.filter(raspberry_pi__last_seen__lte=timezone.now() - datetime.timedelta(hours=14), pi_delivered=True).exclude(status='Banned')
                if value == 'offline_2days':
                    entries = entries.filter(raspberry_pi__last_seen__lte=timezone.now() - datetime.timedelta(hours=14 + 2 * 24), pi_delivered=True).exclude(status='Banned')
                if value == 'offline_5days':
                    entries = entries.filter(raspberry_pi__last_seen__lte=timezone.now() - datetime.timedelta(hours=14 + 5 * 24), pi_delivered=True).exclude(status='Banned')

            if form.cleaned_data['tunnel_state']:
                value = form.cleaned_data['tunnel_state']
                if value == 'online':
                    entries = entries.filter(raspberry_pi__tunnel_last_tested__gt=timezone.now() - datetime.timedelta(hours=14), pi_delivered=True).exclude(status='Banned')
                if value == 'offline':
                    entries = entries.filter(raspberry_pi__tunnel_last_tested__lte=timezone.now() - datetime.timedelta(hours=14), pi_delivered=True).exclude(status='Banned')
                if value == 'offline_2days':
                    entries = entries.filter(raspberry_pi__tunnel_last_tested__lte=timezone.now() - datetime.timedelta(hours=14 + 2 * 24), pi_delivered=True).exclude(status='Banned')
                if value == 'offline_5days':
                    entries = entries.filter(raspberry_pi__tunnel_last_tested__lte=timezone.now() - datetime.timedelta(hours=14 + 5 * 24), pi_delivered=True).exclude(status='Banned')

            if form.cleaned_data['wrong_password']:
                value = form.cleaned_data['wrong_password']
                if value == 'no':
                    entries = entries.filter(wrong_password=False, pi_delivered=True).exclude(status='Banned')
                if value == 'yes':
                    entries = entries.filter(wrong_password=True, pi_delivered=True).exclude(status='Banned')
                if value == 'yes_2days':
                    entries = entries.filter(wrong_password=True, pi_delivered=True, raspberry_pi__last_seen__lte=timezone.now() - datetime.timedelta(hours=14 + 2 * 24)).exclude(status='Banned')
                if value == 'yes_5days':
                    entries = entries.filter(wrong_password=True, pi_delivered=True, raspberry_pi__last_seen__lte=timezone.now() - datetime.timedelta(hours=14 + 5 * 24)).exclude(status='Banned')

            if form.cleaned_data['lead_status']:
                value = form.cleaned_data['lead_status']
                entries = entries.filter(status=value)

            return render(request, 'dashboard.html', dict(
                utm_source=request.user.utm_source,
                entries=entries.order_by('-raspberry_pi__last_seen')[:100],
                form=form,
            ))
