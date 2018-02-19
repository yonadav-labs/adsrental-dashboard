
from __future__ import unicode_literals

import datetime
from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.utils import timezone
from django.contrib.admin import SimpleListFilter

from adsrental.models.lead import Lead
from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.models.ec2_instance import EC2Instance


class LeadStatusListFilter(SimpleListFilter):
    title = 'Lead Status'
    parameter_name = 'lead_status'

    def lookups(self, request, model_admin):
        return Lead.STATUS_CHOICES + [
            ('Active',  'Active'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'Active':
            return queryset.filter(lead__status__in=Lead.STATUSES_ACTIVE)
        if self.value():
            return queryset.filter(lead__status=self.value())


class StatusListFilter(SimpleListFilter):
    title = 'Status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return Lead.STATUS_CHOICES + [
            ('Active',  'Active'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'Active':
            return queryset.filter(status__in=Lead.STATUSES_ACTIVE)
        if self.value():
            return queryset.filter(status=self.value())


class TouchCountListFilter(SimpleListFilter):
    title = 'Touch Count'
    parameter_name = 'touch_count'

    def lookups(self, request, model_admin):
        return (
            ('less10', 'Less than 10 only'),
            ('more10', '10 or more'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'less10':
            return queryset.filter(touch_count__lt=10)
        if self.value() == 'more10':
            return queryset.filter(touch_count__gte=10)


class RaspberryPiOnlineListFilter(SimpleListFilter):
    title = 'RaspberryPi online state'
    parameter_name = 'online'

    def lookups(self, request, model_admin):
        return (
            ('online', 'Online only'),
            ('offline', 'Offline only'),
            ('offline_2days', 'Offline for last 2 days'),
            ('offline_5days', 'Offline for last 5 days'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'online':
            return queryset.filter(raspberry_pi__last_seen__gt=timezone.now() - datetime.timedelta(hours=RaspberryPi.online_hours_ttl))
        if self.value() == 'offline':
            return queryset.filter(raspberry_pi__last_seen__lte=timezone.now() - datetime.timedelta(hours=RaspberryPi.online_hours_ttl))
        if self.value() == 'offline_2days':
            return queryset.filter(raspberry_pi__last_seen__lte=timezone.now() - datetime.timedelta(hours=RaspberryPi.online_hours_ttl + 2 * 24))
        if self.value() == 'offline_5days':
            return queryset.filter(raspberry_pi__last_seen__lte=timezone.now() - datetime.timedelta(hours=RaspberryPi.online_hours_ttl + 5 * 24))


class RaspberryPiFirstTestedListFilter(SimpleListFilter):
    title = 'Shipped Date'
    parameter_name = 'shipped_date'

    def lookups(self, request, model_admin):
        return (
            ('this_week',  'This week'),
            ('previous_week',  'Previous week'),
            ('this_month',  'This month'),
            ('previous_month',  'Previous month'),
            ('not_shipped',  'Not yet'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'this_week':
            end_date = timezone.now()
            start_date = (end_date - datetime.timedelta(days=end_date.weekday())).replace(hour=0, minute=0, second=0)
            return queryset.filter(raspberry_pi__first_tested__gte=start_date, raspberry_pi__first_tested__lte=end_date)
        if self.value() == 'previous_week':
            now = timezone.now()
            end_date = (now - datetime.timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0)
            start_date = end_date - datetime.timedelta(hours=24 * 7)
            return queryset.filter(raspberry_pi__first_tested__gte=start_date, raspberry_pi__first_tested__lte=end_date)
        if self.value() == 'this_month':
            end_date = timezone.now()
            start_date = end_date.replace(day=1, hour=0, minute=0, second=0)
            return queryset.filter(raspberry_pi__first_tested__gte=start_date, raspberry_pi__first_tested__lte=end_date)
        if self.value() == 'previous_month':
            now = timezone.now()
            end_date = now.replace(day=1, hour=0, minute=0, second=0)
            start_date = (end_date - datetime.timedelta(hours=1)).replace(day=1, hour=0, minute=0, second=0)
            return queryset.filter(raspberry_pi__first_tested__gte=start_date, raspberry_pi__first_tested__lte=end_date)
        if self.value() == 'not_shipped':
            return queryset.filter(raspberry_pi__first_tested__isnull=True)


class OnlineListFilter(SimpleListFilter):
    title = 'RaspberryPi online state'
    parameter_name = 'online'

    def lookups(self, request, model_admin):
        return (
            ('online', 'Online only'),
            ('offline', 'Offline only'),
            ('offline_2days', 'Offline for last 2 days'),
            ('offline_5days', 'Offline for last 5 days'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'online':
            return queryset.filter(last_seen__gt=timezone.now() - datetime.timedelta(hours=RaspberryPi.online_hours_ttl))
        if self.value() == 'offline':
            return queryset.filter(last_seen__lte=timezone.now() - datetime.timedelta(hours=RaspberryPi.online_hours_ttl))
        if self.value() == 'offline_2days':
            return queryset.filter(last_seen__lte=timezone.now() - datetime.timedelta(hours=RaspberryPi.online_hours_ttl + 2 * 24))
        if self.value() == 'offline_5days':
            return queryset.filter(last_seen__lte=timezone.now() - datetime.timedelta(hours=RaspberryPi.online_hours_ttl + 5 * 24))


class AccountTypeListFilter(SimpleListFilter):
    title = 'Account type'
    parameter_name = 'account_type'

    def lookups(self, request, model_admin):
        return (
            ('facebook', 'Facebook'),
            ('google', 'Google'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'facebook':
            return queryset.filter(facebook_account=True)
        if self.value() == 'google':
            return queryset.filter(google_account=True)


class TunnelOnlineListFilter(SimpleListFilter):
    title = 'Tunnel online state'
    parameter_name = 'tunnel_online'

    def lookups(self, request, model_admin):
        return (
            ('online', 'Online only'),
            ('offline', 'Offline only'),
            ('offline_2days', 'Offline for last 2 days'),
            ('offline_5days', 'Offline for last 5 days'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'online':
            return queryset.filter(tunnel_last_tested__gt=timezone.now() - datetime.timedelta(hours=RaspberryPi.tunnel_online_hours_ttl))
        if self.value() == 'offline':
            return queryset.filter(tunnel_last_tested__lte=timezone.now() - datetime.timedelta(hours=RaspberryPi.tunnel_online_hours_ttl))
        if self.value() == 'offline_2days':
            return queryset.filter(tunnel_last_tested__lte=timezone.now() - datetime.timedelta(hours=RaspberryPi.tunnel_online_hours_ttl + 2 * 24))
        if self.value() == 'offline_5days':
            return queryset.filter(tunnel_last_tested__lte=timezone.now() - datetime.timedelta(hours=RaspberryPi.tunnel_online_hours_ttl + 5 * 24))


class WrongPasswordListFilter(SimpleListFilter):
    title = 'Wrong Password'
    parameter_name = 'wrong_password'

    def lookups(self, request, model_admin):
        return (
            ('no', 'No'),
            ('yes', 'Yes'),
            ('yes_2days', 'Yes for 2 days'),
            ('yes_5days', 'Yes for 5 days'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'no':
            return queryset.filter(wrong_password_date__isnull=True)
        if self.value() == 'yes':
            return queryset.filter(wrong_password_date__isnull=False)
        if self.value() == 'yes_2days':
            return queryset.filter(wrong_password_date__lte=timezone.now() - datetime.timedelta(hours=2 * 24))
        if self.value() == 'yes_5days':
            return queryset.filter(wrong_password_date__lte=timezone.now() - datetime.timedelta(hours=5 * 24))


class LeadRaspberryPiOnlineListFilter(SimpleListFilter):
    title = 'RaspberryPi online state'
    parameter_name = 'online'

    def lookups(self, request, model_admin):
        return (
            ('online', 'Online'),
            ('online_5m', 'Online last 5 min'),
            ('online_24h', 'Online last 24 hours'),
            ('offline', 'Offline'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'online':
            return queryset.filter(lead__raspberry_pi__last_seen__gt=timezone.now() - datetime.timedelta(hours=RaspberryPi.online_hours_ttl))
        if self.value() == 'online_5m':
            return queryset.filter(lead__raspberry_pi__last_seen__gt=timezone.now() - datetime.timedelta(minutes=5))
        if self.value() == 'online_24h':
            return queryset.filter(lead__raspberry_pi__last_seen__gt=timezone.now() - datetime.timedelta(hours=24))
        if self.value() == 'offline':
            return queryset.filter(lead__raspberry_pi__last_seen__lte=timezone.now() - datetime.timedelta(hours=RaspberryPi.online_hours_ttl))


class LeadRaspberryPiVersionListFilter(SimpleListFilter):
    title = 'RaspberryPi version'
    parameter_name = 'version'

    def lookups(self, request, model_admin):
        return (
            ('latest', 'Only {}'.format(settings.RASPBERRY_PI_VERSION)),
            ('old', 'Old versions'),
            ('null', 'Not set'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'latest':
            return queryset.filter(lead__raspberry_pi__version=settings.RASPBERRY_PI_VERSION)
        if self.value() == 'old':
            return queryset.filter(version__isnull=False).exclude(lead__raspberry_pi__version=settings.RASPBERRY_PI_VERSION)
        if self.value() == 'null':
            return queryset.filter(lead__raspberry_pi__version__isnull=True)


class DateMonthListFilter(SimpleListFilter):
    title = 'Date'
    parameter_name = 'date'

    def lookups(self, request, model_admin):
        month_start = datetime.date.today().replace(day=1)
        choices = []
        for i in range(3):
            d = month_start - relativedelta(months=i)
            choices.append((d.strftime(settings.SYSTEM_DATE_FORMAT), d.strftime('%b %Y')))

        return choices

    def queryset(self, request, queryset):
        if self.value():
            d = datetime.datetime.strptime(self.value(), settings.SYSTEM_DATE_FORMAT).date()
            return queryset.filter(date=d)


class HistoryStatusListFilter(SimpleListFilter):
    title = 'Status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('hide_zeroes', 'Hide zeroes', ),
        )

    def queryset(self, request, queryset):
        if self.value() == 'hide_zeroes':
            return queryset.filter(days_online__gt=0)


class LastTroubleshootListFilter(SimpleListFilter):
    title = 'Lead Troubleshoot'
    parameter_name = 'last_troubleshoot'

    def lookups(self, request, model_admin):
        return (
            ('20minutes', 'Less than 20 minutes ago'),
            ('1hour', 'Less than 1 hour ago'),
            ('5hours', 'Less than 5 hours ago'),
            ('1day', 'Less than 1 day ago'),
            ('older', 'Older'),
        )

    def queryset(self, request, queryset):
        if self.value() == '20minutes':
            return queryset.filter(last_troubleshoot__gte=timezone.now() - datetime.timedelta(minutes=20))
        if self.value() == '1hour':
            return queryset.filter(last_troubleshoot__gte=timezone.now() - datetime.timedelta(hours=1))
        if self.value() == '5hours':
            return queryset.filter(last_troubleshoot__gte=timezone.now() - datetime.timedelta(hours=5))
        if self.value() == '1day':
            return queryset.filter(last_troubleshoot__gte=timezone.now() - datetime.timedelta(hours=24))
        if self.value() == 'older':
            return queryset.filter(last_troubleshoot__lt=timezone.now() - datetime.timedelta(hours=24))


class VersionListFilter(SimpleListFilter):
    title = 'Version'
    parameter_name = 'version'

    def lookups(self, request, model_admin):
        return (
            ('latest', 'Only {}'.format(settings.RASPBERRY_PI_VERSION)),
            ('old', 'Old versions'),
            ('null', 'Not set'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'latest':
            return queryset.filter(version=settings.RASPBERRY_PI_VERSION)
        if self.value() == 'old':
            return queryset.filter(version__isnull=False).exclude(version=settings.RASPBERRY_PI_VERSION)
        if self.value() == 'null':
            return queryset.filter(version__isnull=True)


class TunnelUpListFilter(SimpleListFilter):
    title = 'Tunnel Up'
    parameter_name = 'tunnel_up'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
            ('no_1hour', 'No for 1 hour'),
            ('no_1day', 'No for 1 day'),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'yes':
            return queryset.filter(tunnel_up_date__gt=now - datetime.timedelta(seconds=EC2Instance.TUNNEL_UP_TTL_SECONDS))
        if self.value() == 'no':
            return queryset.filter(tunnel_up_date__lte=now - datetime.timedelta(seconds=EC2Instance.TUNNEL_UP_TTL_SECONDS))
        if self.value() == 'no_1hour':
            return queryset.filter(tunnel_up_date__lte=now - datetime.timedelta(seconds=60 * 60))
        if self.value() == 'no_1day':
            return queryset.filter(tunnel_up_date__lte=now - datetime.timedelta(seconds=60 * 60 * 24))
