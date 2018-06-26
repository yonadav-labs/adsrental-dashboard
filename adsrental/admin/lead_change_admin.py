from __future__ import unicode_literals

from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from adsrental.models.lead_change import LeadChange


class LeadChangeAdmin(admin.ModelAdmin):
    model = LeadChange
    list_display = (
        'id',
        'lead_field',
        'lead_account_field',
        'field',
        'value',
        'old_value',
        'edited_by',
        'created',
    )
    list_select_related = ('lead', )
    list_filter = (
        'field',
    )
    search_fields = ('lead__leadid', 'lead__first_name', 'lead__last_name', 'lead__raspberry_pi__rpid', )

    def lead_field(self, obj):
        lead = obj.lead
        if not lead:
            return None
        return mark_safe('<a target="_blank" href="{url}?q={q}">{text}</a>'.format(
            url=reverse('admin:adsrental_lead_changelist'),
            text=lead.name(),
            q=lead.email,
        ))

    def lead_account_field(self, obj):
        lead_account = obj.lead_account
        if not lead_account:
            return None
        return mark_safe('<a target="_blank" href="{url}?q={q}">{text}</a>'.format(
            url=reverse('admin:adsrental_leadaccount_changelist'),
            text=lead_account.username,
            q=lead_account.username,
        ))

    lead_field.short_description = 'Lead'

    lead_account_field.short_description = 'Lead Account'
