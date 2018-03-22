from __future__ import unicode_literals

import datetime
from urllib.parse import urlencode

from django.views import View
from django.urls import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from adsrental.models.lead import Lead
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
        is_facebook_account = lead.facebook_account
        is_google_account = lead.google_account
        form = SetPasswordForm(initial=dict(
            id=lead.leadid,
            lead_email=lead.email,
            email=lead.fb_email if is_facebook_account else lead.google_email,
            new_password=lead.fb_secret if is_facebook_account else lead.google_password,
        ))
        return render(request, 'dashboard_lead_password.html', dict(
            form=form,
            lead=lead,
            is_facebook_account=is_facebook_account,
            is_google_account=is_google_account,
        ))

    @method_decorator(login_required)
    def post(self, request, lead_id):
        form = SetPasswordForm(request.POST)
        lead = Lead.objects.get(leadid=lead_id)
        is_facebook_account = lead.facebook_account
        is_google_account = lead.google_account
        if form.is_valid():
            if is_facebook_account:
                old_value = lead.fb_secret
                lead.fb_secret = form.cleaned_data['new_password']
                value = lead.fb_secret
                LeadChange(lead=lead, field='fb_secret', value=value, old_value=old_value, edited_by=request.user).save()
            if is_google_account:
                old_value = lead.google_password
                lead.google_password = form.cleaned_data['new_password']
                value = lead.google_password
                LeadChange(lead=lead, field='google_password', value=value, old_value=old_value, edited_by=request.user).save()
            lead.wrong_password = False
            lead.wrong_password_date = None
            lead.save()
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
        if not user.utm_source:
            return Lead.objects.all().select_related('raspberry_pi')

        return Lead.objects.filter(utm_source=user.utm_source).select_related('raspberry_pi')

    @method_decorator(login_required)
    def get(self, request):
        form = DashboardForm(request.GET)
        entries = []
        if form.is_valid():
            entries = self.get_entries(request.user)
            if form.cleaned_data['ec2_state']:
                value = form.cleaned_data['ec2_state']
                entries = entries.filter(pi_delivered=True).exclude(status=Lead.STATUS_BANNED)
                if value == 'online':
                    entries = entries.filter(
                        raspberry_pi__last_seen__gte=timezone.now() - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl),
                    )
                if value == 'offline':
                    entries = entries.filter(
                        raspberry_pi__last_seen__lt=timezone.now() - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl),
                    )
                if value == 'offline_2days':
                    entries = entries.filter(
                        raspberry_pi__last_seen__lt=timezone.now() - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl + 2 * 24 * 60),
                    )
                if value == 'offline_5days':
                    entries = entries.filter(
                        raspberry_pi__last_seen__lt=timezone.now() - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl + 5 * 24 * 60),
                    )

            if form.cleaned_data['wrong_password']:
                value = form.cleaned_data['wrong_password']
                entries = entries.filter(pi_delivered=True).exclude(status=Lead.STATUS_BANNED)
                if value == 'no':
                    entries = entries.filter(
                        wrong_password_date__isnull=True)
                if value == 'yes':
                    entries = entries.filter(
                        wrong_password_date__isnull=False)
                if value == 'yes_0_2days':
                    entries = entries.filter(
                        wrong_password_date__gte=timezone.now() - datetime.timedelta(hours=2 * 24),
                    )
                if value == 'yes_3_5days':
                    entries = entries.filter(
                        wrong_password_date__lte=timezone.now() - datetime.timedelta(hours=2 * 24),
                        wrong_password_date__gte=timezone.now() - datetime.timedelta(hours=5 * 24),
                    )
                if value == 'yes_5days':
                    entries = entries.filter(
                        wrong_password_date__lte=timezone.now() - datetime.timedelta(hours=5 * 24),
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
