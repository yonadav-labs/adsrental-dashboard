from django.contrib import admin, messages
from django.urls import reverse
from django.db.models import Count
from django.utils.safestring import mark_safe

from adsrental.models.bundler import Bundler
from adsrental.models.lead import Lead
from adsrental.admin.list_filters import AbstractUIDListFilter


class IDListFilter(AbstractUIDListFilter):
    parameter_name = 'id'
    title = 'ID'


class BundlerAdmin(admin.ModelAdmin):
    model = Bundler
    list_display = (
        'id',
        'name',
        'utm_source',
        'adsdb_id',
        'email',
        'phone',
        'is_active',
        'leads_count',
        'enable_chargeback',
        'facebook_payment_field',
        'facebook_screenshot_payment_field',
        'google_payment_field',
        'amazon_payment_field',
        'parent_bundler',
        'second_parent_bundler',
        'links',
    )
    actions = (
        'assign_leads_for_this_bundler',
        'pause',
        'activate',
        'enable_chargeback',
        'disable_chargeback',
    )
    search_fields = ('utm_source', 'email', 'name', )
    list_filter = (
        IDListFilter,
        'is_active',
    )

    def get_queryset(self, request):
        queryset = super(BundlerAdmin, self).get_queryset(request)
        return queryset.annotate(leads_count=Count('lead'))

    def pause(self, request, queryset):
        'Inactivate bundler and prevent leads registration for his utm_source'
        for bundler in queryset:
            if bundler.is_active:
                bundler.is_active = False
                bundler.save()
                messages.success(request, 'Bundler {} is now inactive. Leads will not be registered for UTM source {}.'.format(
                    bundler,
                    bundler.utm_source,
                ))

    def activate(self, request, queryset):
        'Activate bundler and allow leads registration for his utm_source'
        for bundler in queryset:
            if not bundler.is_active:
                bundler.is_active = True
                bundler.save()
                messages.success(request, 'Bundler {} is now inactive. Leads can now not be registered for UTM source {}.'.format(
                    bundler,
                    bundler.utm_source,
                ))

    def enable_chargeback(self, request, queryset):
        'Enable chargeback for selected bundlers'
        queryset.update(enable_chargeback=True)

    def disable_chargeback(self, request, queryset):
        'Disable chargeback for selected bundlers'
        queryset.update(enable_chargeback=False)

    def assign_leads_for_this_bundler(self, request, queryset):
        for bundler in queryset:
            leads = Lead.objects.filter(utm_source=bundler.utm_source)
            if leads:
                leads.update(bundler=bundler)
                messages.success(request, 'Bundler {} is assigned to {} leads.'.format(
                    bundler, leads.count(),
                ))
            else:
                messages.success(request, 'Bundler {} has no leads.'.format(
                    bundler,
                ))
            leads = Lead.objects.filter(bundler=bundler).exclude(utm_source=bundler.utm_source)
            if leads:
                leads.update(bundler=None)
                messages.success(request, 'Bundler {} is unassigned from {} leads.'.format(
                    bundler, leads.count(),
                ))

    def leads_count(self, obj):
        return obj.leads_count

    def links(self, obj):
        result = []
        result.append('<a target="_blank" href="{payments_url}">Payments</a>'.format(payments_url=reverse('bundler_payments', kwargs={'bundler_id': obj.id})))
        result.append('<a target="_blank" href="{payments_url}">Reports list</a>'.format(payments_url=reverse('bundler_report_payments_list', kwargs={'bundler_id': obj.id})))
        result.append('<a target="_blank" href="{report_url}">Leaderboard</a>'.format(report_url=reverse('bundler_leaderboard', kwargs={'bundler_id': obj.id})))
        result.append('<a target="_blank" href="{report_url}">Check report</a>'.format(report_url=reverse('bundler_report_check', kwargs={'bundler_id': obj.id})))
        return mark_safe(', '.join(result))

    def facebook_payment_field(self, obj):
        result = []
        if obj.second_parent_bundler:
            result.append('${} / ${} / ${}'.format(
                obj.facebook_payment - obj.facebook_parent_payment - obj.facebook_second_parent_payment,
                obj.facebook_parent_payment,
                obj.facebook_second_parent_payment,
            ))
        elif obj.parent_bundler:
            result.append('${} / ${}'.format(obj.facebook_payment - obj.facebook_parent_payment, obj.facebook_parent_payment))
        else:
            result.append('${}'.format(obj.facebook_payment))

        if obj.enable_chargeback and obj.facebook_chargeback:
            result.append('(CB ${})'.format(obj.facebook_chargeback))

        return ' '.join(result)

    def facebook_screenshot_payment_field(self, obj):
        result = []
        if obj.second_parent_bundler:
            result.append('${} / ${} / ${}'.format(
                obj.facebook_payment - obj.facebook_screenshot_parent_payment - obj.facebook_screenshot_second_parent_payment,
                obj.facebook_screenshot_parent_payment,
                obj.facebook_screenshot_second_parent_payment,
            ))
        elif obj.parent_bundler:
            result.append('${} / ${}'.format(obj.facebook_screenshot_payment - obj.facebook_screenshot_parent_payment, obj.facebook_screenshot_parent_payment))
        else:
            result.append('${}'.format(obj.facebook_screenshot_payment))

        if obj.enable_chargeback and obj.facebook_screenshot_chargeback:
            result.append('(CB ${})'.format(obj.facebook_screenshot_chargeback))

        return ' '.join(result)

    def google_payment_field(self, obj):
        result = []
        if obj.second_parent_bundler:
            result.append('${} / ${} / ${}'.format(
                obj.google_payment - obj.google_parent_payment - obj.google_second_parent_payment,
                obj.google_parent_payment,
                obj.google_second_parent_payment,
            ))
        elif obj.parent_bundler:
            result.append('${} / ${}'.format(obj.google_payment - obj.google_parent_payment, obj.google_parent_payment))
        else:
            result.append('${}'.format(obj.google_payment))

        if obj.enable_chargeback and obj.google_chargeback:
            result.append('(CB ${})'.format(obj.google_chargeback))

        return ' '.join(result)

    def amazon_payment_field(self, obj):
        result = []
        if obj.second_parent_bundler:
            result.append('${} / ${} / ${}'.format(
                obj.amazon_payment - obj.amazon_parent_payment - obj.amazon_second_parent_payment,
                obj.amazon_parent_payment,
                obj.amazon_second_parent_payment,
            ))
        elif obj.parent_bundler:
            result.append('${} / ${}'.format(obj.amazon_payment - obj.amazon_parent_payment, obj.amazon_parent_payment))
        else:
            result.append('${}'.format(obj.amazon_payment))

        if obj.enable_chargeback and obj.amazon_chargeback:
            result.append('(CB ${})'.format(obj.amazon_chargeback))

        return ' '.join(result)

    leads_count.short_description = 'Leads'

    facebook_payment_field.short_description = 'Facebook payment'
    facebook_payment_field.admin_order_field = 'facebook_payment'

    google_payment_field.short_description = 'Google payment'
    google_payment_field.admin_order_field = 'google_payment'

    amazon_payment_field.short_description = 'Amazon payment'
    amazon_payment_field.admin_order_field = 'amazon_payment'
