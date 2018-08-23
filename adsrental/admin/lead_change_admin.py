from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Value
from django.db.models.functions import Concat

from adsrental.models.lead_change import LeadChange

from adsrental.admin.list_filters import AbstractUIDListFilter


class LeadLeadidListFilter(AbstractUIDListFilter):
    parameter_name = 'lead__leadid'
    title = 'Lead ID'


class LeadAccountIDListFilter(AbstractUIDListFilter):
    parameter_name = 'lead_account_id'
    title = 'LeadAccount ID'


class LeadChangeAdmin(admin.ModelAdmin):
    model = LeadChange
    list_display = (
        'id',
        'lead_link',
        'lead_account_field',
        'field',
        'value',
        'old_value',
        'edited_by',
        'data',
        'created',
    )
    list_select_related = ('lead', )
    list_filter = (
        'field',
        LeadLeadidListFilter,
        LeadAccountIDListFilter,
    )
    search_fields = ('lead__email', 'lead__raspberry_pi__rpid', )

    def lead_link(self, obj):
        lead = obj.lead
        if not lead:
            return None
        return mark_safe('<a target="_blank" href="{url}?leadid={q}">{text}</a>'.format(
            url=reverse('admin:adsrental_lead_changelist'),
            text=lead.name(),
            q=lead.leadid,
        ))

    def lead_account_field(self, obj):
        lead_account = obj.lead_account
        if not lead_account:
            return None
        return mark_safe('<a href="{url}?id={id}">{type} {username} ({status})</a>'.format(
            url=reverse('admin:adsrental_leadaccount_changelist'),
            type=lead_account.get_account_type_display(),
            username=lead_account.username,
            status=lead_account.status,
            id=lead_account.id,
        ))

    lead_link.short_description = 'Lead'
    lead_link.admin_order_field = Concat('lead__first_name', Value(' '), 'lead__last_name')

    lead_account_field.short_description = 'Lead Account'
    lead_account_field.admin_order_field = 'lead_account__username'
