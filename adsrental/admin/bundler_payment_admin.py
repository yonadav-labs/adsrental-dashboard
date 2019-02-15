import html

from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from adsrental.models.bundler_payment import BundlerPayment


class BundlerPaymentAdmin(admin.ModelAdmin):
    model = BundlerPayment
    list_display = (
        'id',
        'lead_account_field',
        'bundler_field',
        'payment',
        'payment_type',
        'report',
        'created',
    )
    list_filter = (
        'payment_type',
        'bundler',
    )

    def lead_account_field(self, obj):
        lead_account = obj.lead_account
        if not lead_account:
            return None
        return mark_safe('<a href="{url}?id={id}">{type} {username}</a>{note}'.format(
            url=reverse('admin:adsrental_leadaccount_changelist'),
            type=lead_account.get_account_type_display(),
            username=lead_account.username,
            id=lead_account.id,
            note=f' <img src="/static/admin/img/icon-unknown.svg" title="{html.escape(lead_account.note)}" alt="?">' if lead_account.note else '',
        ))

    def bundler_field(self, obj):
        return mark_safe('<a href="{url}?q={search}">{value}</a>'.format(
            url=reverse('admin:adsrental_bundler_changelist'),
            search=html.escape(obj.bundler.name),
            value=obj.bundler,
        ))

    lead_account_field.short_description = 'Lead Account'
    lead_account_field.admin_order_field = 'lead_account__username'

    bundler_field.short_description = 'Bundler'
    bundler_field.admin_order_field = 'bundler__name'
