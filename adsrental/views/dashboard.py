from __future__ import unicode_literals

import datetime
from urllib.parse import urlencode

from django.views import View
from django.db.models import Q
from django.urls import reverse
from django.shortcuts import render, redirect, Http404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from adsrental.models.lead import Lead
from adsrental.models.lead_account import LeadAccount
from adsrental.models.lead_change import LeadChange
from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.forms import DashboardForm, SetPasswordForm


class CheckSentView(View):
    @method_decorator(login_required)
    def post(self, request):
        lead_id = request.POST.get('leadid')
        lead = Lead.objects.get(leadid=lead_id)
        lead.pi_sent = timezone.now()
        lead.save()
        return redirect('dashboard')


class SetPasswordView(View):
    @method_decorator(login_required)
    def get(self, request, lead_id):
        lead = Lead.objects.get(leadid=lead_id)
        lead_account = lead.lead_accounts.filter(active=True, wrong_password_date__isnull=False).first()
        if not lead_account:
            raise Http404
        form = SetPasswordForm(initial=dict(
            leadid=lead.leadid,
            lead_email=lead.email,
            email=lead_account.username,
            new_password=lead_account.password,
        ))
        return render(request, 'dashboard_lead_password.html', dict(
            form=form,
            lead=lead,
        ))

    @method_decorator(login_required)
    def post(self, request, lead_id):
        form = SetPasswordForm(request.POST)
        lead = Lead.objects.get(leadid=lead_id)
        if form.is_valid():
            lead_account = lead.lead_accounts.filter(active=True, wrong_password_date__isnull=False).first()
            if not lead_account:
                raise Http404
            old_value = lead_account.password
            lead_account.password = form.cleaned_data['new_password']
            lead_account.wrong_password_date = None
            lead_account.save()
            value = lead_account.password
            LeadChange(lead=lead, field='password', value=value, old_value=old_value, edited_by=request.user).save()
            return HttpResponseRedirect('{}?{}'.format(
                reverse('dashboard'),
                urlencode(dict(
                    search=lead.email,
                )),
            ))

        return render(request, 'dashboard_lead_password.html', dict(
            form=form,
            lead=lead,
        ))


class DashboardView(View):
    items_per_page = 100

    def get_entries(self, user):
        queryset = Lead.objects.all()
        if user.bundler:
            queryset = queryset.filter(bundler=user.bundler)

        if user.allowed_raspberry_pis:
            raspberry_pis = user.allowed_raspberry_pis.all()
            queryset = queryset.filter(raspberry_pi__in=raspberry_pis)

        return queryset.prefetch_related('raspberry_pi', 'lead_accounts')

    @method_decorator(login_required)
    def get(self, request):
        form = DashboardForm(request.GET)
        now = timezone.now()
        entries = []
        if form.is_valid():
            entries = self.get_entries(request.user)
            if form.cleaned_data['raspberry_pi_status']:
                value = form.cleaned_data['raspberry_pi_status']
                entries = entries.filter(pi_delivered=True).exclude(status=Lead.STATUS_BANNED)
                if value == 'online':
                    entries = entries.filter(
                        raspberry_pi__last_seen__gte=now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl),
                    )
                if value == 'offline':
                    entries = entries.filter(Q(
                        raspberry_pi__last_seen__lte=now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl),
                    ) | Q(
                        raspberry_pi__last_seen__isnull=True,
                    ))
                if value == 'offline_0_2days':
                    entries = entries.filter(
                        raspberry_pi__last_seen__lte=now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl),
                        raspberry_pi__last_seen__gte=now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl + 2 * 24 * 60),
                    )
                if value == 'offline_3_5days':
                    entries = entries.filter(
                        raspberry_pi__last_seen__lte=now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl + 2 * 24 * 60),
                        raspberry_pi__last_seen__gte=now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl + 5 * 24 * 60),
                    )
                if value == 'offline_5days':
                    entries = entries.filter(
                        raspberry_pi__last_seen__lte=now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl + 5 * 24 * 60),
                    )
                if value == 'never':
                    entries = entries.filter(
                        raspberry_pi__last_seen__isnull=True,
                    )

            if form.cleaned_data['wrong_password']:
                value = form.cleaned_data['wrong_password']
                entries = entries.filter(pi_delivered=True).exclude(status=Lead.STATUS_BANNED)
                if value == 'no':
                    entries = entries.filter(
                        lead_account__wrong_password_date__isnull=True)
                if value == 'yes':
                    entries = entries.filter(
                        lead_account__wrong_password_date__isnull=False)
                if value == 'yes_0_2days':
                    entries = entries.filter(
                        lead_account__wrong_password_date__gte=timezone.now() - datetime.timedelta(hours=2 * 24),
                    )
                if value == 'yes_3_5days':
                    entries = entries.filter(
                        lead_account__wrong_password_date__lte=timezone.now() - datetime.timedelta(hours=2 * 24),
                        lead_account__wrong_password_date__gte=timezone.now() - datetime.timedelta(hours=5 * 24),
                    )
                if value == 'yes_5days':
                    entries = entries.filter(
                        lead_account__wrong_password_date__lte=timezone.now() - datetime.timedelta(hours=5 * 24),
                    )

            if form.cleaned_data['security_checkpoint']:
                value = form.cleaned_data['security_checkpoint']
                if value == 'no':
                    entries = entries.filter(
                        lead_account__security_checkpoint_date__isnull=True)
                if value == 'yes':
                    entries = entries.filter(
                        lead_account__security_checkpoint_date__isnull=False)
                if value == 'yes_0_2days':
                    entries = entries.filter(
                        lead_account__security_checkpoint_date__gte=timezone.now() - datetime.timedelta(hours=2 * 24),
                    )
                if value == 'yes_3_5days':
                    entries = entries.filter(
                        lead_account__security_checkpoint_date__lte=timezone.now() - datetime.timedelta(hours=2 * 24),
                        lead_account__security_checkpoint_date__gte=timezone.now() - datetime.timedelta(hours=5 * 24),
                    )
                if value == 'yes_5days':
                    entries = entries.filter(
                        lead_account__security_checkpoint_date__lte=timezone.now() - datetime.timedelta(hours=5 * 24),
                    )

            if form.cleaned_data['lead_status']:
                value = form.cleaned_data['lead_status']
                entries = entries.filter(status=value)

            if form.cleaned_data['banned']:
                value = form.cleaned_data['banned']
                if value == 'false':
                    entries = entries.exclude(status=Lead.STATUS_BANNED)
                if value == 'true':
                    entries = entries.filter(status=Lead.STATUS_BANNED)

            if form.cleaned_data['pi_delivered']:
                value = form.cleaned_data['pi_delivered']
                if value == 'false':
                    entries = entries.filter(pi_delivered=False)
                if value == 'true':
                    entries = entries.filter(pi_delivered=True)

            if form.cleaned_data['search']:
                value = form.cleaned_data['search']
                entries = entries.filter(Lead.get_fulltext_filter(value, ['raspberry_pi__rpid', 'first_name', 'last_name', 'email', 'phone']))

            if form.cleaned_data['account_type']:
                value = form.cleaned_data['account_type']
                if value == 'facebook':
                    entries = entries.filter(lead_account__account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK)
                if value == 'google':
                    entries = entries.filter(lead_account__account_type=LeadAccount.ACCOUNT_TYPE_GOOGLE)

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
            utm_source=request.user.bundler and request.user.bundler.utm_source,
            entries=entries,
            form=form,
        ))
