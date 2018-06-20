import html

from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from adsrental.models.bundler_lead_stat import BundlerLeadStat


class BundlerLeadStatsAdmin(admin.ModelAdmin):
    model = BundlerLeadStat
    list_display = (
        'id',
        'bundler_field',
        'in_progress_total_field',
        'in_progress_offline_field',
        'in_progress_wrong_pw_field',
        'in_progress_security_checkpoint_field',
        'in_progress_total_issue_percent',
        'autobans_last_30_days_field',
        'other_bans_last_30_days_field',
        'qualified_today_field',
        'qualified_yesterday_field',
        'qualified_last_30_days_field',
        'qualified_total_field',
        'delivered_not_connected',
        'banned_from_qualified_last_30_days',
        'delivered_not_connected_last_30_days',
        'delivered_connected_last_30_days_percent',
    )
    list_select_related = ('bundler', )
    actions = (
        'calculate',
    )
    change_list_template = 'admin/change_list_total.html'

    def bundler_field(self, obj):
        return mark_safe('<a href="{url}?q={search}">{value}</a>'.format(
            url=reverse('admin:adsrental_bundler_changelist'),
            search=html.escape(obj.bundler.name),
            value=obj.bundler,
        ))

    def in_progress_total_field(self, obj):
        return mark_safe('<a href="{url}?account_type__exact=Facebook&status=In-Progress&bundler={bundler_id}">{value}</a>'.format(
            url=reverse('admin:adsrental_leadaccount_changelist'),
            bundler_id=obj.bundler_id,
            value=obj.in_progress_total,
        ))

    def in_progress_offline_field(self, obj):
        return mark_safe('<a href="{url}?account_type__exact=Facebook&status=In-Progress&online=offline&bundler={bundler_id}">{value}</a>'.format(
            url=reverse('admin:adsrental_leadaccount_changelist'),
            bundler_id=obj.bundler_id,
            value=obj.in_progress_offline,
        ))

    def in_progress_wrong_pw_field(self, obj):
        return mark_safe('<a href="{url}?account_type__exact=Facebook&status=In-Progress&wrong_password=yes&bundler={bundler_id}">{value}</a>'.format(
            url=reverse('admin:adsrental_leadaccount_changelist'),
            bundler_id=obj.bundler_id,
            value=obj.in_progress_wrong_pw,
        ))

    def in_progress_security_checkpoint_field(self, obj):
        return mark_safe('<a href="{url}?account_type__exact=Facebook&status=In-Progress&security_checkpoint=yes&bundler={bundler_id}">{value}</a>'.format(
            url=reverse('admin:adsrental_leadaccount_changelist'),
            bundler_id=obj.bundler_id,
            value=obj.in_progress_security_checkpoint,
        ))

    def autobans_last_30_days_field(self, obj):
        return mark_safe('<a href="{url}?account_type__exact=Facebook&auto_ban=yes&banned_date=last_30_days&bundler={bundler_id}">{value}</a>'.format(
            url=reverse('admin:adsrental_leadaccount_changelist'),
            bundler_id=obj.bundler_id,
            value=obj.autobans_last_30_days,
        ))

    def other_bans_last_30_days_field(self, obj):
        return mark_safe('<a href="{url}?account_type__exact=Facebook&auto_ban=no&banned_date=last_30_days&bundler={bundler_id}">{value}</a>'.format(
            url=reverse('admin:adsrental_leadaccount_changelist'),
            bundler_id=obj.bundler_id,
            value=obj.bans_last_30_days - obj.autobans_last_30_days,
        ))

    def qualified_today_field(self, obj):
        return mark_safe('<a href="{url}?account_type__exact=Facebook&qualified_date=today&bundler={bundler_id}">{value}</a>'.format(
            url=reverse('admin:adsrental_leadaccount_changelist'),
            bundler_id=obj.bundler_id,
            value=obj.qualified_today,
        ))

    def qualified_yesterday_field(self, obj):
        return mark_safe('<a href="{url}?account_type__exact=Facebook&qualified_date=yesterday&bundler={bundler_id}">{value}</a>'.format(
            url=reverse('admin:adsrental_leadaccount_changelist'),
            bundler_id=obj.bundler_id,
            value=obj.qualified_yesterday,
        ))

    def qualified_last_30_days_field(self, obj):
        return mark_safe('<a href="{url}?account_type__exact=Facebook&qualified_date=last_30_days&bundler={bundler_id}">{value}</a>'.format(
            url=reverse('admin:adsrental_leadaccount_changelist'),
            bundler_id=obj.bundler_id,
            value=obj.qualified_last_30_days,
        ))

    def qualified_total_field(self, obj):
        return mark_safe('<a href="{url}?account_type__exact=Facebook&status=Qualified&bundler={bundler_id}">{value}</a>'.format(
            url=reverse('admin:adsrental_leadaccount_changelist'),
            bundler_id=obj.bundler_id,
            value=obj.qualified_total,
        ))

    def in_progress_total_issue_percent(self, obj):
        return '%d%%' % (
            obj.in_progress_total_issue * 100 / max(obj.in_progress_total, 1)
        )

    def delivered_connected_last_30_days_percent(self, obj):
        return '%d%%' % (
            (obj.delivered_last_30_days - obj.delivered_not_connected_last_30_days) * 100 / max(obj.delivered_last_30_days, 1),
        )

    def calculate(self, request, queryset):
        for bundler_lead_stat in queryset:
            BundlerLeadStat.calculate(bundler_lead_stat.bundler)

    bundler_field.short_description = 'Bundler'
    bundler_field.admin_order_field = 'bundler__name'

    in_progress_total_field.short_description = 'Total In-Progress'
    in_progress_total_field.admin_order_field = 'in_progress_total'

    in_progress_offline_field.short_description = 'Offline In-Progress'
    in_progress_offline_field.admin_order_field = 'in_progress_offline'

    in_progress_wrong_pw_field.short_description = 'Wrong PW In-Progress'
    in_progress_wrong_pw_field.admin_order_field = 'in_progress_wrong_pw'

    in_progress_security_checkpoint_field.short_description = 'Sec Checkpoint In-Progress'
    in_progress_security_checkpoint_field.admin_order_field = 'in_progress_security_checkpoint'

    in_progress_total_field.short_description = 'Total issue In-Progress'
    in_progress_total_field.admin_order_field = 'in_progress_total'

    autobans_last_30_days_field.short_description = 'Auto bans (last 30 days)'
    autobans_last_30_days_field.admin_order_field = 'in_progress_total'

    other_bans_last_30_days_field.short_description = 'Other bans (last 30 days)'
    other_bans_last_30_days_field.admin_order_field = 'bans_last_30_days'

    qualified_today_field.short_description = 'Qualified today'
    qualified_today_field.admin_order_field = 'qualified_today'

    qualified_yesterday_field.short_description = 'Qualified yesterday'
    qualified_yesterday_field.admin_order_field = 'qualified_yesterday'

    qualified_last_30_days_field.short_description = 'Qualified last 30 days'
    qualified_last_30_days_field.admin_order_field = 'qualified_last_30_days'

    qualified_total_field.short_description = 'Qualified total'
    qualified_total_field.admin_order_field = 'qualified_total'

    delivered_connected_last_30_days_percent.short_description = 'Delivered and connected (last 30 days)'
    delivered_connected_last_30_days_percent.admin_order_field = 'delivered_last_30_days'
