import datetime

from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
    items_per_page = 100

    def get_entries(self, user):
        if not user.utm_source:
            return Lead.objects.all().select_related('raspberry_pi')

        return Lead.objects.filter(utm_source=user.utm_source).select_related('raspberry_pi')

    @method_decorator(login_required)
    def get(self, request):
        form = DashboardForm(request.GET)
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

            if form.cleaned_data['banned']:
                value = form.cleaned_data['banned']
                if value == 'false':
                    entries = entries.exclude(status='Banned')
                if value == 'true':
                    entries = entries.filter(status='Banned')

            if form.cleaned_data['pi_delivered']:
                value = form.cleaned_data['pi_delivered']
                if value == 'false':
                    entries = entries.filter(pi_delivered=False)
                if value == 'true':
                    entries = entries.filter(pi_delivered=True)

            if form.cleaned_data['search']:
                value = form.cleaned_data['search']
                entries = entries.filter(
                    Q(raspberry_pi__rpid__icontains=value) |
                    Q(first_name__icontains=value) |
                    Q(last_name__icontains=value) |
                    Q(email__icontains=value)
                )

            if form.cleaned_data['account_type']:
                value = form.cleaned_data['account_type']
                if value == 'facebook':
                    entries = entries.filter(facebook_account=True)
                if value == 'google':
                    entries = entries.filter(google_account=True)

            order = request.GET.get('order', '-raspberry_pi__last_seen')
            entries = entries.order_by(order)

            page = request.GET.get('page', 1)
            paginator = Paginator(entries, self.items_per_page)
            try:
                entries = paginator.page(page)
            except PageNotAnInteger:
                entries = paginator.page(1)
            except EmptyPage:
                entries = paginator.page(paginator.num_pages)

            return render(request, 'dashboard.html', dict(
                utm_source=request.user.utm_source,
                entries=entries,
                form=form,
            ))
