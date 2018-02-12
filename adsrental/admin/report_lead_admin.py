from __future__ import unicode_literals

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.contrib.humanize.templatetags.humanize import naturaltime

from adsrental.models.lead import ReportProxyLead
from adsrental.admin.list_filters import StatusListFilter, RaspberryPiOnlineListFilter, TouchCountListFilter, AccountTypeListFilter


class ReportLeadAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }

    model = ReportProxyLead
    list_display = (
        'leadid',
        # 'rpid',
        'first_name',
        'last_name',
        # 'utm_source',
        'status',
        # 'street',
        # 'city',
        # 'state',
        # 'postal_code',
        'pi_delivered',
        'is_sync_adsdb',
        'account_type',
        'company',
        'email',
        # 'phone',
        'raspberry_pi_link',
        'utm_source',
        'bundler_paid',
        'billed',
        'touch_count',
        'last_touch',
        'wrong_password',
        'first_seen',
        'last_seen',
    )
    list_filter = (
        StatusListFilter,
        'company',
        AccountTypeListFilter,
        RaspberryPiOnlineListFilter,
        TouchCountListFilter,
        'is_sync_adsdb',
        'bundler_paid',
        'pi_delivered',
    )
    readonly_fields = ('created', 'updated', )
    search_fields = ('leadid', 'account_name', 'first_name', 'last_name', 'raspberry_pi__rpid', 'email', )
    list_select_related = ('raspberry_pi', )
    list_per_page = 500

    def rpid(self, obj):
        return obj.raspberry_pi and obj.raspberry_pi.rpid

    def account_type(self, obj):
        if obj.facebook_account:
            return 'Facebook'
        if obj.google_account:
            return 'Google'
        return 'n/a'

    def first_seen(self, obj):
        return obj.raspberry_pi and obj.raspberry_pi.first_seen

    def last_seen(self, obj):
        return obj.raspberry_pi and obj.raspberry_pi.last_seen

    def last_touch(self, obj):
        return '<span title="Touched {} times">{}</span>'.format(
            obj.touch_count,
            naturaltime(obj.last_touch_date) if obj.last_touch_date else 'Never',
        )

    def raspberry_pi_link(self, obj):
        result = []
        if obj.raspberry_pi:
            result.append('<a target="_blank" href="{url}?q={rpid}">{rpid}</a>'.format(
                url=reverse('admin:adsrental_raspberrypi_changelist'),
                rpid=obj.raspberry_pi,
            ))

        return result

    last_touch.allow_tags = True
    raspberry_pi_link.allow_tags = True

    last_touch.admin_order_field = 'last_touch_date'
    raspberry_pi_link.admin_order_field = 'raspberry_pi__rpid'
    first_seen.admin_order_field = 'raspberry_pi__first_seen'
    last_seen.admin_order_field = 'raspberry_pi__last_seen'
    account_type.admin_order_field = 'facebook_account'

    raspberry_pi_link.short_description = 'RPID'
