
from __future__ import unicode_literals

import datetime
from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Count
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _

from adsrental.models.lead import Lead
from adsrental.models.lead_account import LeadAccount
from adsrental.models.bundler import Bundler
from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.models.ec2_instance import EC2Instance


class LeadStatusListFilter(SimpleListFilter):
    title = 'Lead Status'
    parameter_name = 'lead_status'

    def lookups(self, request, model_admin):
        return Lead.STATUS_CHOICES + [
            ('Active', 'Active'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'Active':
            return queryset.filter(lead__status__in=Lead.STATUSES_ACTIVE)
        if self.value():
            return queryset.filter(lead__status=self.value())
        return None


class StatusListFilter(SimpleListFilter):
    title = 'Status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return Lead.STATUS_CHOICES + [
            ('Active', 'Active'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'Active':
            return queryset.filter(status__in=Lead.STATUSES_ACTIVE)
        if self.value():
            return queryset.filter(status=self.value())
        return None


class TouchCountListFilter(SimpleListFilter):
    title = 'Touch Count'
    parameter_name = 'touch_count'

    def lookups(self, request, model_admin):
        return (
            ('less5', 'Less than 5 only'),
            ('more5', '5 or more'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'less5':
            return queryset.filter(touch_count__lt=5)
        if self.value() == 'more5':
            return queryset.filter(touch_count__gte=5)
        return None


class LeadAccountTouchCountListFilter(SimpleListFilter):
    title = 'Touch Count'
    parameter_name = 'touch_count'

    def lookups(self, request, model_admin):
        return (
            ('less5', 'Less than 5 only'),
            ('more5', '5 or more'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'less5':
            return queryset.filter(lead_account__touch_count__lt=5)
        if self.value() == 'more5':
            return queryset.filter(lead_account__touch_count__gte=5)
        return None


class DeliveryDateListFilter(SimpleListFilter):
    title = 'Delivery Date'
    parameter_name = 'delivery_date'

    def lookups(self, request, model_admin):
        return (
            ('this_week', 'This week'),
            ('previous_week', 'Previous week'),
            ('this_month', 'This month'),
            ('previous_month', 'Previous month'),
            ('not', 'Not yet'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'this_week':
            end_date = timezone.now()
            start_date = (end_date - datetime.timedelta(days=end_date.weekday())).replace(hour=0, minute=0, second=0)
            return queryset.filter(delivery_date__gte=start_date, delivery_date__lte=end_date)
        if self.value() == 'previous_week':
            now = timezone.now()
            end_date = (now - datetime.timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0)
            start_date = end_date - datetime.timedelta(hours=24 * 7)
            return queryset.filter(delivery_date__gte=start_date, delivery_date__lte=end_date)
        if self.value() == 'this_month':
            end_date = timezone.now()
            start_date = end_date.replace(day=1, hour=0, minute=0, second=0)
            return queryset.filter(delivery_date__gte=start_date, delivery_date__lte=end_date)
        if self.value() == 'previous_month':
            now = timezone.now()
            end_date = now.replace(day=1, hour=0, minute=0, second=0)
            start_date = (end_date - datetime.timedelta(hours=1)).replace(day=1, hour=0, minute=0, second=0)
            return queryset.filter(delivery_date__gte=start_date, delivery_date__lte=end_date)
        if self.value() == 'not':
            return queryset.filter(delivery_date__isnull=True)
        return None


class OnlineListFilter(SimpleListFilter):
    title = 'RaspberryPi online state'
    parameter_name = 'online'
    filter_field = 'last_seen'

    def lookups(self, request, model_admin):
        return (
            ('online', 'Online only'),
            ('offline', 'Offline only'),
            ('offline_0_2days', 'Offline for 0-2 days'),
            ('offline_3_5days', 'Offline for 3-5 days'),
            ('offline_5days', 'Offline for more than 5 days'),
            ('never', 'Never'),
        )

    def queryset(self, request, queryset):  # pylint: disable=R0911
        filter_field__gte = '{}__gte'.format(self.filter_field)
        filter_field__lte = '{}__lte'.format(self.filter_field)
        filter_field__isnull = '{}__isnull'.format(self.filter_field)
        if self.value() == 'online':
            return queryset.filter(**{
                filter_field__gte: timezone.now() - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl),
            })
        if self.value() == 'offline':
            return queryset.filter(Q(**{
                filter_field__lte: timezone.now() - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl),
            }) | Q(**{
                filter_field__isnull: True,
            }))
        if self.value() == 'offline_0_2days':
            now = timezone.now()
            return queryset.filter(**{
                filter_field__lte: now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl),
                filter_field__gte: now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl + 2 * 24 * 60),
            })
        if self.value() == 'offline_3_5days':
            now = timezone.now()
            return queryset.filter(**{
                filter_field__lte: now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl + 2 * 24 * 60),
                filter_field__gte: now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl + 5 * 24 * 60),
            })
        if self.value() == 'offline_5days':
            return queryset.filter(**{
                filter_field__lte: timezone.now() - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl + 5 * 24 * 60),
            })
        if self.value() == 'never':
            return queryset.filter(**{
                filter_field__isnull: True,
            })
        return None


class RaspberryPiOnlineListFilter(OnlineListFilter):
    filter_field = 'raspberry_pi__last_seen'


class LeadRaspberryPiOnlineListFilter(OnlineListFilter):
    filter_field = 'lead__raspberry_pi__last_seen'


class ShipDateListFilter(SimpleListFilter):
    title = 'Shipped date'
    parameter_name = 'shipped_date'

    def lookups(self, request, model_admin):
        return (
            ('current_week', 'Current week', ),
            ('previus_week', 'Previous week', ),
            ('current_month', 'Current month', ),
            ('previus_month', 'Previous month', ),
        )

    def queryset(self, request, queryset):
        if self.value() == 'current_week':
            now = timezone.now()
            current_week_start = now - datetime.timedelta(days=now.weekday())
            return queryset.filter(
                ship_date__gte=current_week_start.date(),
            )
        if self.value() == 'previous_week':
            now = timezone.now()
            current_week_start = now - datetime.timedelta(days=now.weekday())
            prev_week_end = current_week_start - datetime.timedelta(days=1)
            prev_week_start = prev_week_end - datetime.timedelta(days=prev_week_end.weekday())
            return queryset.filter(
                ship_date__gte=prev_week_start.date(),
                ship_date__lte=prev_week_end.date(),
            )
        if self.value() == 'current_month':
            now = timezone.now()
            current_month_start = now - datetime.timedelta(days=now.day - 1)
            return queryset.filter(
                ship_date__gte=current_month_start.date(),
            )
        if self.value() == 'previous_week':
            now = timezone.now()
            current_month_start = now - datetime.timedelta(days=now.day - 1)
            prev_month_end = current_month_start - datetime.timedelta(days=1)
            prev_month_start = prev_month_end - datetime.timedelta(days=prev_month_end.day - 1)
            return queryset.filter(
                ship_date__gte=prev_month_start.date(),
                ship_date__lte=prev_month_end.date(),
            )
        return None


class QualifiedDateListFilter(SimpleListFilter):
    title = 'Qualified date'
    parameter_name = 'qualified_date'
    field_name = 'qualified_date'

    def lookups(self, request, model_admin):
        return (
            ('today', 'Today', ),
            ('yesterday', 'Yesterday', ),
            ('last_30_days', 'Last 30 days', ),
            ('current_week', 'Current week', ),
            ('previus_week', 'Previous week', ),
            ('current_month', 'Current month', ),
            ('previus_month', 'Previous month', ),
        )

    def queryset(self, request, queryset):
        if self.value() == 'today':
            now = timezone.now()
            date_start = now.replace(hour=0, minute=0, second=0)
            return queryset.filter(**{
                '{}__gte'.format(self.field_name): date_start,
            })
        if self.value() == 'yesterday':
            now = timezone.now()
            date_end = now.replace(hour=0, minute=0, second=0)
            date_start = date_end - datetime.timedelta(days=1)
            return queryset.filter(**{
                '{}__gte'.format(self.field_name): date_start,
                '{}__lte'.format(self.field_name): date_end,
            })
        if self.value() == 'last_30_days':
            now = timezone.now()
            date_start = now - datetime.timedelta(days=30)
            return queryset.filter(**{
                '{}__gte'.format(self.field_name): date_start,
            })
        if self.value() == 'current_week':
            now = timezone.now()
            date_start = now - datetime.timedelta(days=now.weekday())
            return queryset.filter(**{
                '{}__gte'.format(self.field_name): date_start,
            })
        if self.value() == 'previous_week':
            now = timezone.now()
            current_week_start = now - datetime.timedelta(days=now.weekday())
            prev_week_end = current_week_start - datetime.timedelta(days=1)
            prev_week_start = prev_week_end - datetime.timedelta(days=prev_week_end.weekday())
            return queryset.filter(**{
                '{}__gte'.format(self.field_name): prev_week_start,
                '{}__lte'.format(self.field_name): prev_week_end,
            })
        if self.value() == 'current_month':
            now = timezone.now()
            current_month_start = now - datetime.timedelta(days=now.day - 1)
            return queryset.filter(**{
                '{}__gte'.format(self.field_name): current_month_start,
            })
        if self.value() == 'previous_week':
            now = timezone.now()
            current_month_start = now - datetime.timedelta(days=now.day - 1)
            prev_month_end = current_month_start - datetime.timedelta(days=1)
            prev_month_start = prev_month_end - datetime.timedelta(days=prev_month_end.day - 1)
            return queryset.filter(**{
                '{}__gte'.format(self.field_name): prev_month_start,
                '{}__lte'.format(self.field_name): prev_month_end,
            })
        return None


class AutoBanListFilter(SimpleListFilter):
    title = 'Auto-ban'
    parameter_name = 'auto_ban'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes', ),
            ('no', 'No', ),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(
                ban_reason__in=LeadAccount.AUTO_BAN_REASONS,
            )
        if self.value() == 'no':
            return queryset.filter(
                ban_reason__isnull=False,
            ).exclude(
                ban_reason__in=LeadAccount.AUTO_BAN_REASONS,
            )


class BannedDateListFilter(SimpleListFilter):
    title = 'Banned date'
    parameter_name = 'banned_date'

    def lookups(self, request, model_admin):
        return (
            ('current_week', 'Current week', ),
            ('previus_week', 'Previous week', ),
            ('current_month', 'Current month', ),
            ('last_30_days', 'Last 30 days', ),
        )

    def queryset(self, request, queryset):
        if self.value() == 'current_week':
            now = timezone.now()
            current_week_start = now - datetime.timedelta(days=now.weekday())
            return queryset.filter(
                banned_date__gte=current_week_start,
            )
        if self.value() == 'previous_week':
            now = timezone.now()
            current_week_start = now - datetime.timedelta(days=now.weekday())
            prev_week_end = current_week_start - datetime.timedelta(days=1)
            prev_week_start = prev_week_end - datetime.timedelta(days=prev_week_end.weekday())
            return queryset.filter(
                banned_date__gte=prev_week_start,
                banned_date__lte=prev_week_end,
            )
        if self.value() == 'current_month':
            now = timezone.now()
            current_month_start = now - datetime.timedelta(days=now.day - 1)
            return queryset.filter(
                banned_date__gte=current_month_start,
            )
        if self.value() == 'last_30_days':
            now = timezone.now()
            date_30_days_ago = now - datetime.timedelta(days=30)
            return queryset.filter(
                banned_date__gte=date_30_days_ago,
            )
        return None


class AccountTypeListFilter(SimpleListFilter):
    title = 'Account type'
    parameter_name = 'account_type'

    def lookups(self, request, model_admin):
        return (
            ('facebook', 'Facebook only'),
            ('google', 'Google only'),
            ('amazon', 'Amazon'),
            ('many', 'Several accounts'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'facebook':
            return queryset.filter(lead_account__account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK).exclude(lead_account__account_type__in=[LeadAccount.ACCOUNT_TYPE_GOOGLE, LeadAccount.ACCOUNT_TYPE_AMAZON])
        if self.value() == 'google':
            return queryset.filter(lead_account__account_type=LeadAccount.ACCOUNT_TYPE_GOOGLE).exclude(lead_account__account_type__in=[LeadAccount.ACCOUNT_TYPE_FACEBOOK, LeadAccount.ACCOUNT_TYPE_AMAZON])
        if self.value() == 'amazon':
            return queryset.filter(lead_account__account_type=LeadAccount.ACCOUNT_TYPE_AMAZON)
        if self.value() == 'many':
            return queryset.annotate(lead_accounts_count=Count('lead_account')).filter(lead_accounts_count__gt=1)
        return None


class WrongPasswordListFilter(SimpleListFilter):
    title = 'Wrong Password'
    parameter_name = 'wrong_password'

    def lookups(self, request, model_admin):
        return (
            ('no', 'No'),
            ('yes', 'Yes'),
            ('yes_0_2days', 'Wrong for 0-2 days'),
            ('yes_3_5days', 'Wrong for 3-5 days'),
            ('yes_5days', 'Wrong for more than 5 days'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'no':
            return queryset.filter(wrong_password_date__isnull=True)
        if self.value() == 'yes':
            return queryset.filter(wrong_password_date__isnull=False)
        if self.value() == 'yes_0_2days':
            return queryset.filter(
                wrong_password_date__gte=timezone.now() - datetime.timedelta(hours=2 * 24),
            )
        if self.value() == 'yes_3_5days':
            return queryset.filter(
                wrong_password_date__lte=timezone.now() - datetime.timedelta(hours=2 * 24),
                wrong_password_date__gte=timezone.now() - datetime.timedelta(hours=5 * 24),
            )
        if self.value() == 'yes_5days':
            return queryset.filter(
                wrong_password_date__lte=timezone.now() - datetime.timedelta(hours=5 * 24),
            )
        return None


class LeadAccountWrongPasswordListFilter(SimpleListFilter):
    title = 'Wrong Password'
    parameter_name = 'wrong_password'

    def lookups(self, request, model_admin):
        return (
            ('no', 'No'),
            ('yes', 'Yes'),
            ('yes_0_2days', 'Wrong for 0-2 days'),
            ('yes_3_5days', 'Wrong for 3-5 days'),
            ('yes_5days', 'Wrong for more than 5 days'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'no':
            return queryset.filter(lead_account__wrong_password_date__isnull=True)
        if self.value() == 'yes':
            return queryset.filter(lead_account__wrong_password_date__isnull=False)
        if self.value() == 'yes_0_2days':
            return queryset.filter(
                lead_account__wrong_password_date__gte=timezone.now() - datetime.timedelta(hours=2 * 24),
            )
        if self.value() == 'yes_3_5days':
            return queryset.filter(
                lead_account__wrong_password_date__lte=timezone.now() - datetime.timedelta(hours=2 * 24),
                lead_account__wrong_password_date__gte=timezone.now() - datetime.timedelta(hours=5 * 24),
            )
        if self.value() == 'yes_5days':
            return queryset.filter(
                lead_account__wrong_password_date__lte=timezone.now() - datetime.timedelta(hours=5 * 24),
            )
        return None


class SecurityCheckpointListFilter(SimpleListFilter):
    title = 'Security Checkpoint reported'
    parameter_name = 'security_checkpoint'

    def lookups(self, request, model_admin):
        return (
            ('no', 'No'),
            ('yes', 'Reported'),
            ('yes_0_2days', 'Reported for 0-2 days'),
            ('yes_3_5days', 'Reported for 3-5 days'),
            ('yes_5days', 'Reported for more than 5 days'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'no':
            return queryset.filter(security_checkpoint_date__isnull=True)
        if self.value() == 'yes':
            return queryset.filter(security_checkpoint_date__isnull=False)
        if self.value() == 'yes_0_2days':
            return queryset.filter(
                security_checkpoint_date__gte=timezone.now() - datetime.timedelta(hours=2 * 24),
            )
        if self.value() == 'yes_3_5days':
            return queryset.filter(
                security_checkpoint_date__lte=timezone.now() - datetime.timedelta(hours=2 * 24),
                security_checkpoint_date__gte=timezone.now() - datetime.timedelta(hours=5 * 24),
            )
        if self.value() == 'yes_5days':
            return queryset.filter(
                security_checkpoint_date__lte=timezone.now() - datetime.timedelta(hours=5 * 24),
            )
        return None


class LeadAccountSecurityCheckpointListFilter(SimpleListFilter):
    title = 'Security Checkpoint reported'
    parameter_name = 'security_checkpoint'

    def lookups(self, request, model_admin):
        return (
            ('no', 'No'),
            ('yes', 'Reported'),
            ('yes_0_2days', 'Reported for 0-2 days'),
            ('yes_3_5days', 'Reported for 3-5 days'),
            ('yes_5days', 'Reported for more than 5 days'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'no':
            return queryset.filter(lead_account__security_checkpoint_date__isnull=True)
        if self.value() == 'yes':
            return queryset.filter(lead_account__security_checkpoint_date__isnull=False)
        if self.value() == 'yes_0_2days':
            return queryset.filter(
                lead_account__security_checkpoint_date__gte=timezone.now() - datetime.timedelta(hours=2 * 24),
            )
        if self.value() == 'yes_3_5days':
            return queryset.filter(
                lead_account__security_checkpoint_date__lte=timezone.now() - datetime.timedelta(hours=2 * 24),
                lead_account__security_checkpoint_date__gte=timezone.now() - datetime.timedelta(hours=5 * 24),
            )
        if self.value() == 'yes_5days':
            return queryset.filter(
                lead_account__security_checkpoint_date__lte=timezone.now() - datetime.timedelta(hours=5 * 24),
            )
        return None


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
        return None


class DateMonthListFilter(SimpleListFilter):
    title = 'Date'
    parameter_name = 'date'

    def lookups(self, request, model_admin):
        month_start = datetime.date.today().replace(day=1)
        choices = []
        for i in range(3):
            date_month = month_start - relativedelta(months=i)
            choices.append((date_month.strftime(settings.SYSTEM_DATE_FORMAT), date_month.strftime('%b %Y')))

        return choices

    def get_month_end(self, date):
        if date.month == 12:
            return date.replace(day=31)
        return date.replace(month=date.month+1, day=1) - datetime.timedelta(days=1)

    def queryset(self, request, queryset):
        if self.value():
            month_start = datetime.datetime.strptime(self.value(), settings.SYSTEM_DATE_FORMAT).date()
            month_end = self.get_month_end(month_start)
            return queryset.filter(
                date__gte=month_start,
                date__lte=month_end,
            )
        return None


class AmountListFilter(SimpleListFilter):
    title = 'Amount'
    parameter_name = 'amount'

    def lookups(self, request, model_admin):
        return (
            ('gt_0', 'Hide $0', ),
            ('gte_2', '$2 or more', ),
        )

    def queryset(self, request, queryset):
        if self.value() == 'gt_0':
            return queryset.filter(amount__gt=0)
        if self.value() == 'gte_2':
            return queryset.filter(amount__gte=2)
        return None


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
        return None


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
        return None


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
            return queryset.filter(
                Q(tunnel_up_date__lte=now - datetime.timedelta(seconds=EC2Instance.TUNNEL_UP_TTL_SECONDS)) |
                Q(tunnel_up_date__isnull=True, lead__raspberry_pi__last_seen__isnull=False)
            )
        if self.value() == 'no_1hour':
            return queryset.filter(tunnel_up_date__lte=now - datetime.timedelta(seconds=60 * 60))
        if self.value() == 'no_1day':
            return queryset.filter(tunnel_up_date__lte=now - datetime.timedelta(seconds=60 * 60 * 24))
        return None


class BundlerListFilter(SimpleListFilter):
    title = 'Bundler'
    parameter_name = 'bundler'
    template = 'admin/checkbox_filter.html'

    def choices(self, changelist):
        current_value = self.value()
        values = current_value
        yield {
            'selected': self.value() is None,
            'query_string': changelist.get_query_string({}, [self.parameter_name]),
            'display': _('All'),
        }
        for lookup, title in self.lookup_choices:
            lookup_value = []
            if lookup not in values:
                lookup_value.extend(current_value)
                lookup_value.append(lookup)
            else:
                for value in current_value:
                    if value != lookup:
                        lookup_value.append(value)

            lookup_value = ','.join([str(i) for i in lookup_value if i])
            if lookup_value:
                yield {
                    'selected': lookup in current_value,
                    'query_string': changelist.get_query_string({self.parameter_name: lookup_value}, []),
                    'display': title,
                }
            else:
                yield {
                    'selected': lookup in current_value,
                    'query_string': changelist.get_query_string({}, [self.parameter_name]),
                    'display': title,
                }
        yield {
            'selected': 0 in self.value(),
            'query_string': changelist.get_query_string({self.parameter_name: '0'}, []),
            'display': _('Not assigned'),
        }

    def value(self):
        result = self.used_parameters.get(self.parameter_name)
        if not result:
            return []

        return [int(i) for i in result.split(',') if i.isdigit()]

    def lookups(self, request, model_admin):
        choices = [(i[0], '%s (%s)' % i[1:]) for i in Bundler.objects.all().values_list('id', 'name', 'utm_source')]
        return choices

    def queryset(self, request, queryset):
        if self.value() == [0]:
            return queryset.filter(bundler__isnull=True)
        if self.value():
            return queryset.filter(bundler_id__in=self.value())
        return None


class LeadBundlerListFilter(SimpleListFilter):
    title = 'Bundler'
    parameter_name = 'bundler'
    template = 'admin/checkbox_filter.html'

    def choices(self, changelist):
        current_value = self.value()
        values = current_value
        yield {
            'selected': self.value() is None,
            'query_string': changelist.get_query_string({}, [self.parameter_name]),
            'display': _('All'),
        }
        for lookup, title in self.lookup_choices:
            lookup_value = []
            if lookup not in values:
                lookup_value.extend(current_value)
                lookup_value.append(lookup)
            else:
                for value in current_value:
                    if value != lookup:
                        lookup_value.append(value)

            lookup_value = ','.join([str(i) for i in lookup_value if i])
            if lookup_value:
                yield {
                    'selected': lookup in current_value,
                    'query_string': changelist.get_query_string({self.parameter_name: lookup_value}, []),
                    'display': title,
                }
            else:
                yield {
                    'selected': lookup in current_value,
                    'query_string': changelist.get_query_string({}, [self.parameter_name]),
                    'display': title,
                }
        yield {
            'selected': 0 in self.value(),
            'query_string': changelist.get_query_string({self.parameter_name: '0'}, []),
            'display': _('Not assigned'),
        }

    def value(self):
        result = self.used_parameters.get(self.parameter_name)
        if not result:
            return []

        return [int(i) for i in result.split(',') if i.isdigit()]

    def lookups(self, request, model_admin):
        choices = [(i[0], '%s (%s)' % i[1:]) for i in Bundler.objects.all().values_list('id', 'name', 'utm_source')]
        return choices

    def queryset(self, request, queryset):
        if self.value() == [0]:
            return queryset.filter(lead__bundler__isnull=True)
        if self.value():
            return queryset.filter(lead__bundler_id__in=self.value())
        return None
