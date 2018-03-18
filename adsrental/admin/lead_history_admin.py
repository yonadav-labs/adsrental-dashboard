from __future__ import unicode_literals

from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from adsrental.models.lead_history import LeadHistory
from adsrental.admin.list_filters import DateMonthListFilter, LeadStatusListFilter


class LeadHistoryAdmin(admin.ModelAdmin):
    model = LeadHistory
    list_display = ('id', 'lead_link', 'email', 'rpid', 'date', 'active', 'online', 'wrong_password', )
    raw_id_fields = ('lead', )
    list_select_related = ('lead', 'lead__raspberry_pi')
    search_fields = ('lead__email', )
    list_filter = ('date', )

    list_filter = (DateMonthListFilter, LeadStatusListFilter, )

    def lead_link(self, obj):
        lead = obj.lead
        return mark_safe('<a target="_blank" href="{url}?q={q}">{lead}</a>'.format(
            url=reverse('admin:adsrental_lead_changelist'),
            lead=lead.name(),
            q=lead.leadid,
        ))

    def email(self, obj):
        return obj.lead.email

    def rpid(self, obj):
        return obj.lead.raspberry_pi and obj.lead.raspberry_pi.rpid

    def active(self, obj):
        return obj.is_active()

    def online(self, obj):
        return obj.is_online()

    def wrong_password(self, obj):
        return obj.is_wrong_password()

    lead_link.short_description = 'Lead'

    active.boolean = True

    online.boolean = True

    wrong_password.boolean = True
