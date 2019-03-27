import datetime

from django.views import View
from django.shortcuts import render, redirect
from django.db.models import Q, Sum
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from adsrental.models.lead_account import LeadAccount
from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.models.bundler_payment import BundlerPayment
from adsrental.models.bundler import Bundler
from adsrental.forms import DashboardForm
from adsrental.utils import get_week_boundaries_for_dt


class DashboardHomeView(View):
    items_per_page = 100

    def get_entries(self, user, bundler_id):
        queryset = LeadAccount.objects.all()
        if user.bundler:
            queryset = queryset.filter(lead__bundler=user.bundler)

        if user.allowed_raspberry_pis.count():
            raspberry_pis = user.allowed_raspberry_pis.all()
            queryset = queryset.filter(lead__raspberry_pi__in=raspberry_pis)

        if bundler_id:
            queryset = queryset.filter(lead__bundler_id=bundler_id)

        return queryset.prefetch_related('lead', 'lead__raspberry_pi', 'lead__bundler')

    def get_bundlers(self, user, bundler_id):
        if user.bundler:
            return Bundler.objects.filter(id=user.bundler.id)

        if bundler_id:
            return Bundler.objects.filter(id=bundler_id)

        if user.is_superuser:
            return Bundler.objects.all()

        return []

    @method_decorator(login_required)
    def get(self, request, bundler_id=None):
        form = DashboardForm(request.GET)
        now = timezone.localtime(timezone.now())
        week_start, week_end = get_week_boundaries_for_dt(now)
        entries = []
        if not form.is_valid():
            return redirect('dashboard')

        entries = self.get_entries(request.user, bundler_id)
        bundlers = self.get_bundlers(request.user, bundler_id)
        qualified_this_week = LeadAccount.objects.filter(lead__bundler__in=bundlers, qualified_date__gt=week_start, qualified_date__lt=week_end).count()
        payments_this_week = BundlerPayment.objects.filter(bundler__in=bundlers, created__gt=week_start, created__lt=week_end).aggregate(total=Sum('payment'))

        if form.cleaned_data['raspberry_pi_status']:
            value = form.cleaned_data['raspberry_pi_status']
            if value == 'online':
                entries = entries.filter(
                    lead__raspberry_pi__last_seen__gte=now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl),
                )
            if value == 'offline':
                entries = entries.filter(Q(
                    lead__raspberry_pi__last_seen__lte=now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl),
                ) | Q(
                    lead__raspberry_pi__last_seen__isnull=True,
                ))
            if value == 'offline_0_2days':
                entries = entries.filter(
                    lead__raspberry_pi__last_seen__lte=now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl),
                    lead__raspberry_pi__last_seen__gte=now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl + 2 * 24 * 60),
                )
            if value == 'offline_3_5days':
                entries = entries.filter(
                    lead__raspberry_pi__last_seen__lte=now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl + 2 * 24 * 60),
                    lead__raspberry_pi__last_seen__gte=now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl + 5 * 24 * 60),
                )
            if value == 'offline_5days':
                entries = entries.filter(
                    lead__raspberry_pi__last_seen__lte=now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl + 5 * 24 * 60),
                )
            if value == 'never':
                entries = entries.filter(
                    lead__raspberry_pi__last_seen__isnull=True,
                )

        if form.cleaned_data['wrong_password']:
            value = form.cleaned_data['wrong_password']
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

        if form.cleaned_data['security_checkpoint']:
            value = form.cleaned_data['security_checkpoint']
            if value == 'no':
                entries = entries.filter(
                    security_checkpoint_date__isnull=True)
            if value == 'yes':
                entries = entries.filter(
                    security_checkpoint_date__isnull=False)
            if value == 'yes_0_2days':
                entries = entries.filter(
                    security_checkpoint_date__gte=timezone.now() - datetime.timedelta(hours=2 * 24),
                )
            if value == 'yes_3_5days':
                entries = entries.filter(
                    security_checkpoint_date__lte=timezone.now() - datetime.timedelta(hours=2 * 24),
                    security_checkpoint_date__gte=timezone.now() - datetime.timedelta(hours=5 * 24),
                )
            if value == 'yes_5days':
                entries = entries.filter(
                    security_checkpoint_date__lte=timezone.now() - datetime.timedelta(hours=5 * 24),
                )

        if form.cleaned_data['lead_status']:
            value = form.cleaned_data['lead_status']
            entries = entries.filter(status=value)

        if form.cleaned_data['banned']:
            value = form.cleaned_data['banned']
            if value == 'false':
                entries = entries.exclude(status=LeadAccount.STATUS_BANNED)
            if value == 'true':
                entries = entries.filter(status=LeadAccount.STATUS_BANNED)

        if form.cleaned_data['pi_delivered']:
            value = form.cleaned_data['pi_delivered']
            if value == 'last_2_14_days':
                entries = entries.filter(
                    lead__delivery_date__lt=now - datetime.timedelta(days=2),
                    lead__delivery_date__gte=now - datetime.timedelta(days=14),
                )
            if value == 'false':
                entries = entries.filter(lead__delivery_date__isnull=True)
            if value == 'true':
                entries = entries.filter(lead__delivery_date__isnull=False)

        if form.cleaned_data['pi_connected']:
            value = form.cleaned_data['pi_connected']
            if value == 'true':
                entries = entries.filter(
                    lead__raspberry_pi__first_seen__isnull=False,
                )
            if value == 'false':
                entries = entries.filter(
                    lead__raspberry_pi__first_seen__isnull=True,
                )

        if form.cleaned_data['search']:
            value = form.cleaned_data['search']
            entries = entries.filter(LeadAccount.get_fulltext_filter(value, ['lead__raspberry_pi__rpid', 'lead__first_name', 'lead__last_name', 'lead__email', 'lead__phone']))

        if form.cleaned_data['account_type']:
            value = form.cleaned_data['account_type']
            if value == 'facebook':
                entries = entries.filter(account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK)
            if value == 'google':
                entries = entries.filter(account_type=LeadAccount.ACCOUNT_TYPE_GOOGLE)
            if value == 'amazon':
                entries = entries.filter(account_type=LeadAccount.ACCOUNT_TYPE_AMAZON)
            if value == 'facebook_screenshot':
                entries = entries.filter(account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK_SCREENSHOT)

        if form.cleaned_data['shipstation_order_status']:
            value = form.cleaned_data['shipstation_order_status']
            if value:
                entries = entries.filter(lead__shipstation_order_status=value)

        order = request.GET.get('order', '-lead__raspberry_pi__last_seen')
        # entries = entries.prefetch_related('lead', 'lead__raspberry_pi', 'lead__bundler')
        entries = entries.order_by(order)
        total = entries.count()
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
            total=total,
            qualified_this_week=qualified_this_week,
            payments_this_week=payments_this_week,
        ))
