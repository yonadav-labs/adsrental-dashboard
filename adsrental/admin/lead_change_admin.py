from __future__ import unicode_literals

from django.contrib import admin
from django.core.urlresolvers import reverse

from adsrental.models.lead_change import LeadChange


class LeadChangeAdmin(admin.ModelAdmin):
    model = LeadChange
    list_display = (
        'id',
        'lead_link',
        'field',
        'value',
        'old_value',
        'edited_by',
        'created',
    )
    list_select_related = ('lead', )
    list_filter = (
        'value',
        'old_value',
    )

    def lead_link(self, obj):
        lead = obj.lead
        return '<a target="_blank" href="{url}?q={q}">{lead}</a>'.format(
            url=reverse('admin:adsrental_lead_changelist'),
            lead=lead.name(),
            q=lead.leadid,
        )

    lead_link.short_description = 'Lead'
    lead_link.allow_tags = True
