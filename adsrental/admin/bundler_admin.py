from __future__ import unicode_literals

from django.contrib import admin, messages
from django.urls import reverse
from django.db.models import Count
from django.utils.safestring import mark_safe

from adsrental.models.bundler import Bundler
from adsrental.models.lead import Lead


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
        'facebook_payment',
        'google_payment',
        'links',
    )
    actions = (
        'assign_leads_for_this_bundler',
        'pause',
        'activate',
        'enable_chargeback',
        'disable_chargeback',
    )
    search_fields = ('utm_source', 'email', )

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
        result.append('<a target="_blank" href="{payments_url}">Lead Payments</a>'.format(payments_url=reverse('bundler_lead_payments', kwargs={'bundler_id': obj.id})))
        result.append('<a target="_blank" href="{report_url}">Stats</a>'.format(report_url=reverse('bundler_report', kwargs={'bundler_id': obj.id})))
        return mark_safe(', '.join(result))

    leads_count.short_description = 'Leads'
