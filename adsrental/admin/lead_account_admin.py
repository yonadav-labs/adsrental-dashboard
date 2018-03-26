from __future__ import unicode_literals

from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.humanize.templatetags.humanize import naturaltime

from adsrental.models.lead_account import LeadAccount


class LeadAccountAdmin(admin.ModelAdmin):
    model = LeadAccount
    list_display = (
        'id',
        'lead_link',
        'account_type',
        'username',
        'password',
        'bundler_paid',
        'adsdb_account_id',
        'wrong_password_date_field',
        'created',
    )
    list_select_related = ('lead', )
    list_filter = (
        'account_type',
    )
    search_fields = ('lead__leadid', 'username', )

    def lead_link(self, obj):
        lead = obj.lead
        return mark_safe('<a target="_blank" href="{url}?q={q}">{lead}</a>'.format(
            url=reverse('admin:adsrental_lead_changelist'),
            lead=lead.name(),
            q=lead.leadid,
        ))

    def wrong_password_date_field(self, obj):
        if not obj.wrong_password_date:
            return None

        return mark_safe('<span title="{}">{}</span> <a href="{}" target="_blank">Fix</a>'.format(
            obj.wrong_password_date,
            naturaltime(obj.wrong_password_date),
            reverse('dashboard_set_password', kwargs=dict(lead_id=obj.lead.leadid)),
        ))

    lead_link.short_description = 'Lead'
    lead_link.admin_order_field = 'lead__leadid'

    wrong_password_date_field.short_description = 'Wrong Password'
    wrong_password_date_field.admin_order_field = 'wrong_password_date'
