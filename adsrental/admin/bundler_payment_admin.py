import html

from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from adsrental.models.bundler_payment import BundlerPayment
from adsrental.admin.list_filters import AbstractIntIDListFilter


class LeadAccountIDListFilter(AbstractIntIDListFilter):
    parameter_name = 'lead_account_id'
    title = 'LeadAccount ID'


class BundlerPaymentAdmin(admin.ModelAdmin):
    list_per_page = 100
    change_list_template = 'admin/change_list_total.html'

    model = BundlerPayment
    list_display = (
        'id',
        'lead_account_field',
        'bundler_field',
        'payment',
        'payment_type',
        'report',
        'paid',
        'ready',
        'datetime',
    )
    list_filter = (
        LeadAccountIDListFilter,
        'payment_type',
        'paid',
        'bundler',
    )
    list_select_related = ('lead_account', 'bundler', 'report')
    raw_id_fields = ('lead_account', )

    def lead_account_field(self, obj):
        lead_account = obj.lead_account
        if not lead_account:
            return None
        comments = '\n'.join(lead_account.get_comments())
        return mark_safe('<a href="{url}?id={id}">{type} {username}</a>{note}'.format(
            url=reverse('admin:adsrental_leadaccount_changelist'),
            type=lead_account.get_account_type_display(),
            username=lead_account.username,
            id=lead_account.id,
            note=f' <img src="/static/admin/img/icon-unknown.svg" title="{html.escape(comments)}" alt="?">' if comments else '',
        ))

    def bundler_field(self, obj):
        if not obj.bundler:
            return None
        return mark_safe('<a href="{url}?q={search}">{value}</a>'.format(
            url=reverse('admin:adsrental_bundler_changelist'),
            search=html.escape(obj.bundler.name),
            value=obj.bundler,
        ))

    lead_account_field.short_description = 'Lead Account'
    lead_account_field.admin_order_field = 'lead_account__username'

    bundler_field.short_description = 'Bundler'
    bundler_field.admin_order_field = 'bundler__name'
