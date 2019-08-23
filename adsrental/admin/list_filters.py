import datetime
import re
from dateutil import relativedelta, parser

from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Count
from django.contrib.admin import SimpleListFilter, FieldListFilter
from django.utils.translation import ugettext_lazy as _

from adsrental.models.lead import Lead
from adsrental.models.lead_account import LeadAccount
from adsrental.models.bundler import Bundler
from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.models.ec2_instance import EC2Instance
from adsrental.utils import get_week_boundaries_for_dt, get_month_boundaries_for_dt


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


class LeadAccountStatusListFilter(SimpleListFilter):
    title = 'Lead Account Status'
    parameter_name = 'lead_account_status'

    def lookups(self, request, model_admin):
        return LeadAccount.STATUS_CHOICES + [
            ('Active', 'Active'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'Active':
            return queryset.filter(lead_account__status__in=Lead.STATUSES_ACTIVE)
        if self.value():
            return queryset.filter(lead_account__status=self.value())
        return None


class StatusListFilter(SimpleListFilter):
    title = 'Status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return LeadAccount.STATUS_CHOICES + [
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
            ('zero', 'None'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'zero':
            return queryset.filter(touch_count=0)
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
            ('zero', 'None'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'zero':
            return queryset.filter(lead_account__touch_count=0)
        if self.value() == 'less5':
            return queryset.filter(lead_account__touch_count__lt=5)
        if self.value() == 'more5':
            return queryset.filter(lead_account__touch_count__gte=5)
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


class LastTouchDateListFilter(SimpleListFilter):
    title = 'Last Touch Date'
    parameter_name = 'last_touch_date'
    field_name = 'last_touch_date'

    def lookups(self, request, model_admin):
        return (
            ('24_hours', 'Last 0-24 hours', ),
            ('36_hours', 'Last 24-36 hours', ),
            ('more', 'More than 36 hours ago', ),
            ('never', 'Never', ),
        )

    def queryset(self, request, queryset):
        if self.value() == '24_hours':
            now = timezone.localtime(timezone.now())
            return queryset.filter(**{
                f'{self.field_name}__gt': now - datetime.timedelta(hours=24)
            })
        if self.value() == '36_hours':
            now = timezone.localtime(timezone.now())
            return queryset.filter(**{
                f'{self.field_name}__gt': now - datetime.timedelta(hours=36),
                f'{self.field_name}__lt': now - datetime.timedelta(hours=24),
            })
        if self.value() == 'more':
            now = timezone.localtime(timezone.now())
            return queryset.filter(**{
                f'{self.field_name}__lt': now - datetime.timedelta(hours=36),
            })
        if self.value() == 'never':
            return queryset.filter(**{
                f'{self.field_name}__isnull': True,
            })


class AbstractDateListFilter(SimpleListFilter):
    title = 'Date'
    parameter_name = 'date'
    field_name = 'date'

    CHOICES_TODAY = 'today'
    CHOICES_YESTERDAY = 'yesterday'
    CHOICES_LAST_14_DAYS = 'last_14_days'
    CHOICES_LAST_30_DAYS = 'last_30_days'
    CHOICES_CURRENT_WEEK = 'current_week'
    CHOICES_PREVIOUS_WEEK = 'previous_week'
    CHOICES_CURRENT_MONTH = 'current_month'
    CHOICES_PREVIOUS_MONTH = 'previous_month'
    CHOICES_ANY = 'any'
    CHOICES_NOT_SET = 'not_set'

    def lookups(self, request, model_admin):
        return (
            (self.CHOICES_TODAY, 'Today', ),
            (self.CHOICES_YESTERDAY, 'Yesterday', ),
            (self.CHOICES_LAST_14_DAYS, 'Last 14 days', ),
            (self.CHOICES_LAST_30_DAYS, 'Last 30 days', ),
            (self.CHOICES_CURRENT_WEEK, 'Current week', ),
            (self.CHOICES_PREVIOUS_WEEK, 'Previous week', ),
            (self.CHOICES_CURRENT_MONTH, 'Current month', ),
            (self.CHOICES_PREVIOUS_MONTH, 'Previous month', ),
            (self.CHOICES_ANY, 'Any', ),
            (self.CHOICES_NOT_SET, 'Not set', ),
        )

    def queryset(self, request, queryset):
        if self.value() == self.CHOICES_TODAY:
            now = timezone.localtime(timezone.now())
            date_start = now.replace(hour=0, minute=0, second=0)
            return queryset.filter(**{
                '{}__gte'.format(self.field_name): date_start,
            })
        if self.value() == self.CHOICES_YESTERDAY:
            now = timezone.localtime(timezone.now())
            date_end = now.replace(hour=0, minute=0, second=0)
            date_start = date_end - datetime.timedelta(days=1)
            return queryset.filter(**{
                '{}__gte'.format(self.field_name): date_start,
                '{}__lte'.format(self.field_name): date_end,
            })
        if self.value() == self.CHOICES_LAST_14_DAYS:
            now = timezone.localtime(timezone.now())
            date_start = now - datetime.timedelta(days=14)
            return queryset.filter(**{
                '{}__gte'.format(self.field_name): date_start,
            })
        if self.value() == self.CHOICES_LAST_30_DAYS:
            now = timezone.localtime(timezone.now())
            date_start = now - datetime.timedelta(days=30)
            return queryset.filter(**{
                '{}__gte'.format(self.field_name): date_start,
            })
        if self.value() == self.CHOICES_CURRENT_WEEK:
            now = timezone.localtime(timezone.now())
            date_start, _ = get_week_boundaries_for_dt(now)
            return queryset.filter(**{
                '{}__gte'.format(self.field_name): date_start,
            })
        if self.value() == self.CHOICES_PREVIOUS_WEEK:
            now = timezone.localtime(timezone.now())
            date_start, date_end = get_week_boundaries_for_dt(now - datetime.timedelta(days=7))
            return queryset.filter(**{
                '{}__gte'.format(self.field_name): date_start,
                '{}__lte'.format(self.field_name): date_end,
            })
        if self.value() == self.CHOICES_CURRENT_MONTH:
            now = timezone.localtime(timezone.now())
            date_start, _ = get_month_boundaries_for_dt(now)
            return queryset.filter(**{
                '{}__gte'.format(self.field_name): date_start,
            })
        if self.value() == self.CHOICES_PREVIOUS_MONTH:
            now = timezone.localtime(timezone.now())
            current_date_start, _ = get_month_boundaries_for_dt(now)
            date_start, date_end = get_month_boundaries_for_dt(current_date_start - datetime.timedelta(days=1))

            return queryset.filter(**{
                '{}__gte'.format(self.field_name): date_start,
                '{}__lte'.format(self.field_name): date_end,
            })
        if self.value() == self.CHOICES_ANY:
            return queryset.filter(**{
                '{}__isnull'.format(self.field_name): False,
            })
        if self.value() == self.CHOICES_NOT_SET:
            return queryset.filter(**{
                '{}__isnull'.format(self.field_name): True,
            })
        return None


class DeliveryDateListFilter(AbstractDateListFilter):
    title = 'Delivery Date'
    parameter_name = 'delivery_date'
    field_name = 'delivery_date'


class LeadDeliveryDateListFilter(AbstractDateListFilter):
    title = 'Delivery Date'
    parameter_name = 'lead__delivery_date'
    field_name = 'lead__delivery_date'


class ShipDateListFilter(AbstractDateListFilter):
    title = 'Shipped date'
    field_name = 'ship_date'
    parameter_name = 'shipped_date'


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
        return None


class BannedDateListFilter(AbstractDateListFilter):
    title = 'Banned date'
    field_name = 'banned_date'
    parameter_name = 'banned_date'


class AccountTypeListFilter(SimpleListFilter):
    title = 'Account type'
    parameter_name = 'account_type'
    field_name = 'account_type'

    def lookups(self, request, model_admin):
        return (
            ('facebook_only', 'Facebook only'),
            ('facebook_screenshot_only', 'Facebook Screenshot only'),
            ('google_only', 'Google only'),
            ('facebook', 'Facebook'),
            ('facebook_screenshot', 'Facebook Screenshot'),
            ('facebook_types', 'Facebook and Facebook Screenshot'),
            ('google', 'Google'),
            ('amazon', 'Amazon'),
            ('many', 'Several accounts'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'facebook_only':
            return queryset.filter(**{
                self.field_name: LeadAccount.ACCOUNT_TYPE_FACEBOOK
            }).exclude(**{
                f'{self.field_name}__in': [LeadAccount.ACCOUNT_TYPE_FACEBOOK_SCREENSHOT, LeadAccount.ACCOUNT_TYPE_GOOGLE, LeadAccount.ACCOUNT_TYPE_AMAZON],
            })
        if self.value() == 'facebook_screenshot_only':
            return queryset.filter(**{
                self.field_name: LeadAccount.ACCOUNT_TYPE_FACEBOOK_SCREENSHOT
            }).exclude(**{
                f'{self.field_name}__in': [LeadAccount.ACCOUNT_TYPE_FACEBOOK, LeadAccount.ACCOUNT_TYPE_GOOGLE, LeadAccount.ACCOUNT_TYPE_AMAZON]
            })
        if self.value() == 'google_only':
            return queryset.filter(**{
                self.field_name: LeadAccount.ACCOUNT_TYPE_GOOGLE
            }).exclude(**{
                f'{self.field_name}__in': [LeadAccount.ACCOUNT_TYPE_FACEBOOK, LeadAccount.ACCOUNT_TYPE_FACEBOOK_SCREENSHOT, LeadAccount.ACCOUNT_TYPE_AMAZON]
            })
        if self.value() == 'facebook':
            return queryset.filter(**{
                self.field_name: LeadAccount.ACCOUNT_TYPE_FACEBOOK
            })
        if self.value() == 'facebook_screenshot':
            return queryset.filter(**{
                self.field_name: LeadAccount.ACCOUNT_TYPE_FACEBOOK_SCREENSHOT
            })
        if self.value() == 'facebook_types':
            return queryset.filter(**{
                f'{self.field_name}__in': LeadAccount.ACCOUNT_TYPES_FACEBOOK
            })
        if self.value() == 'google':
            return queryset.filter(**{
                self.field_name: LeadAccount.ACCOUNT_TYPE_GOOGLE
            })
        if self.value() == 'amazon':
            return queryset.filter(**{
                self.field_name: LeadAccount.ACCOUNT_TYPE_AMAZON
            })
        return None


class LeadAccountAccountTypeListFilter(AccountTypeListFilter):
    title = 'Account type'
    parameter_name = 'account_type'
    field_name = 'lead_account__account_type'

    def lookups(self, request, model_admin):
        result = super(LeadAccountAccountTypeListFilter, self).lookups(request, model_admin)
        return result + (
            ('many', 'Several accounts'),
        )

    def queryset(self, request, queryset):
        result = super(LeadAccountAccountTypeListFilter, self).queryset(request, queryset)
        if result:
            return result
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
            ('yes_facebook', 'Yes for Facebook'),
            ('yes_google', 'Yes for Google'),
            ('yes_0_2days', 'Wrong for 0-2 days'),
            ('yes_3_5days', 'Wrong for 3-5 days'),
            ('yes_5days', 'Wrong for more than 5 days'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'no':
            return queryset.filter(lead_account__wrong_password_date__isnull=True)
        if self.value() == 'yes':
            return queryset.filter(lead_account__wrong_password_date__isnull=False)
        if self.value() == 'yes_facebook':
            return queryset.filter(lead_account__wrong_password_date__isnull=False, lead_account__account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK)
        if self.value() == 'yes_google':
            return queryset.filter(lead_account__wrong_password_date__isnull=False, lead_account__account_type=LeadAccount.ACCOUNT_TYPE_GOOGLE)
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
        for i in range(6):
            date_month = month_start - relativedelta.relativedelta(months=i)
            choices.append((date_month.strftime(settings.SYSTEM_DATE_FORMAT), date_month.strftime('%b %Y')))

        return choices

    def get_month_end(self, date):
        if date.month == 12:
            return date.replace(day=31)
        return date.replace(month=date.month+1, day=1) - datetime.timedelta(days=1)

    def queryset(self, request, queryset):
        if self.value():
            month_start = parser.parse(self.value()).date()
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
        choices = [(i[0], '%s (%s)' % i[1:]) for i in Bundler.objects.all().order_by('name').values_list('id', 'name', 'utm_source')]
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


class AbstractUIDListFilter(SimpleListFilter):
    parameter_name = 'id'
    title = 'ID'
    template = 'admin/hidden_filter.html'

    def lookups(self, request, model_admin):
        # Dummy, required to show the filter.
        return ((),)

    def choices(self, changelist):
        # Grab only the "all" option.
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )
        yield all_choice

    def queryset(self, request, queryset):
        if self.value():
            value = self.value()
            return queryset.filter(**{
                self.parameter_name: value,
            })
        return None


class AbstractIntIDListFilter(AbstractUIDListFilter):
    def queryset(self, request, queryset):
        if self.value():
            if self.value().isdigit():
                value = self.value()
                return queryset.filter(**{
                    self.parameter_name: value,
                })
            else:
                return queryset.none()
        return None


class AbstractFulltextFilter(AbstractUIDListFilter):
    field_names = []
    _findterms = re.compile(r'"([^"]+)"|(\S+)').findall
    _normspace = re.compile(r'\s{2,}').sub

    def _normalize_query(self, query_string):
        '''
        Splits the query string in invidual keywords, getting rid of unecessary spaces and grouping quoted words together.
        Example:
        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
            ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
        '''

        return [self._normspace('', (t[0] or t[1]).strip()) for t in self._findterms(query_string)]

    def queryset(self, request, queryset):
        if self.value():
            query = None
            terms = self._normalize_query(self.value())
            for term in terms:
                or_query = None
                for field_name in self.field_names:
                    q = Q(**{
                        "{}__icontains".format(field_name): term
                    })
                    if or_query is None:
                        or_query = q
                    else:
                        or_query = or_query | q
                if query is None:
                    query = or_query
                else:
                    query = query & or_query
            return queryset.filter(query)
        return None


def titled_filter(title):
    class Wrapper(FieldListFilter):  # pylint: disable=W0223
        def __new__(cls, *args, **kwargs):
            instance = FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper


class DeliveredLastTwoDaysListFilter(SimpleListFilter):
    parameter_name = 'delivered_last_2_days'
    title = 'Delivered last 2 days'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(
                lead__delivery_date__gt=timezone.now() - datetime.timedelta(days=2),
            )
        if self.value() == 'no':
            return queryset.filter(
                lead__delivery_date__lte=timezone.now() - datetime.timedelta(days=2),
            )
        return None


class EditedByListFilter(SimpleListFilter):
    parameter_name = 'edited_by'
    title = 'Edited by'

    def lookups(self, request, model_admin):
        return (
            (settings.ADSDB_USERNAME, 'Adsdb user'),
            (settings.AUTOBAN_USER_EMAIL, 'Autoban bot'),
            (settings.ADMIN_USER_EMAIL, 'One-time script'),
            (settings.PING_USER_EMAIL, 'Ping bot'),
            ('other', 'Other'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'other':
            return queryset.exclude(
                edited_by__email__in=[settings.ADSDB_USERNAME, settings.AUTOBAN_USER_EMAIL, settings.ADMIN_USER_EMAIL, settings.PING_USER_EMAIL],
            )
        if self.value():
            return queryset.filter(
                edited_by__email=self.value(),
            )
        return None


class ReportedByListFilter(SimpleListFilter):
    parameter_name = 'reported_by'
    title = 'Reporter Type'

    def lookups(self, request, model_admin):
        return (
            ('bundler', 'Bundlers'),
            ('buyer', 'Buyers'),
            ('va', 'VAs'),
            ('admin', 'Admin'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'va':
            return queryset.filter(
                reporter__first_name='VA',
            )
        elif self.value() == 'admin':
            return queryset.filter(
                reporter__is_superuser=True
            )
        elif self.value() == 'buyer':
            ids = [ii.id for ii in queryset if ii.reporter and ii.reporter.groups.filter(name='Buyer').exists()]
            return queryset.filter(id__in=ids)
        elif self.value() == 'bundler':
            ids = [ii.id for ii in queryset if ii.reporter and ii.reporter.groups.filter(name='Bundler').exists()]
            return queryset.filter(id__in=ids)
        return queryset


class ProxyDelayFilter(SimpleListFilter):
    parameter_name = 'proxy_delay'
    title = 'Proxy delay'

    def lookups(self, request, model_admin):
        return (
            ('good', 'Good'),
            ('slow', 'Slow'),
            ('unusable', 'Unusable'),
            ('unreachable', 'Unreachable'),
            ('set', 'Measured'),
            ('unset', 'Not measured'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'good':
            return queryset.filter(
                proxy_delay__isnull=False,
                proxy_delay__lte=2.0,
            )
        if self.value() == 'slow':
            return queryset.filter(
                proxy_delay__isnull=False,
                proxy_delay__gt=2.0,
                proxy_delay__lte=5.0,
            )
        if self.value() == 'unusable':
            return queryset.filter(
                proxy_delay__isnull=False,
                proxy_delay__gte=5.0,
                proxy_delay__lt=900.0,
            )
        if self.value() == 'unreachable':
            return queryset.filter(
                proxy_delay__isnull=False,
                proxy_delay__gt=900.0,
            )
        if self.value() == 'set':
            return queryset.filter(
                proxy_delay__isnull=False,
            )
        if self.value() == 'unset':
            return queryset.filter(
                proxy_delay__isnull=True,
            )
        return queryset
