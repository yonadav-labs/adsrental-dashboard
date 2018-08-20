import datetime

from django.views import View
from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from adsrental.models.lead import Lead
from adsrental.models.lead_account import LeadAccount
from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.forms import DashboardForm


class DashboardHomeView(View):
    items_per_page = 100

    def get_entries(self, user):
        queryset = Lead.objects.all()
        if user.bundler:
            queryset = queryset.filter(bundler=user.bundler)

        if user.allowed_raspberry_pis.count():
            raspberry_pis = user.allowed_raspberry_pis.all()
            queryset = queryset.filter(raspberry_pi__in=raspberry_pis)

        return queryset.prefetch_related('raspberry_pi', 'lead_accounts')

    @method_decorator(login_required)
    def get(self, request):
        form = DashboardForm(request.GET)
        now = timezone.localtime(timezone.now())
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

            if form.cleaned_data['shipstation_order_status']:
                value = form.cleaned_data['shipstation_order_status']
                if value:
                    entries = entries.filter(shipstation_order_status=value)

            order = request.GET.get('order', '-raspberry_pi__last_seen')
            entries = entries.prefetch_related('lead_accounts')
            entries = entries.order_by(order)

            page = request.GET.get('page', 1)
            paginator = Paginator(entries, self.items_per_page)
            try:
                entries = paginator.page(page)
            except PageNotAnInteger:
                entries = paginator.page(1)
            except EmptyPage:
                entries = paginator.page(paginator.num_pages)


        return render(request, 'dashboard/home.html', dict(
            utm_source=request.user.bundler and request.user.bundler.utm_source,
            preset=request.GET.get('preset'),
            entries=entries,
            form=form,
        ))
