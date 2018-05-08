from __future__ import unicode_literals

from django.contrib import admin, messages
from django.urls import reverse
from django.utils.safestring import mark_safe

from adsrental.models.bundler_payments_report import BundlerPaymentsReport


class BundlerPaymentsReportAdmin(admin.ModelAdmin):
    model = BundlerPaymentsReport
    list_display = (
        'id',
        'date',
        'paid',
        'cancelled',
        'email_sent',
        'links',
    )
    search_fields = ('date', )
    actions = (
        'mark_as_paid',
        # 'rollback',
        'send_by_email',
        'mark',
        'unmark',
    )

    def get_actions(self, request):
        actions = super(BundlerPaymentsReportAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def links(self, obj):
        result = []
        result.append('<a target="_blank" href="{url}">View</a>'.format(url=reverse('admin_bundler_report_payments', kwargs=dict(report_id=obj.id))))
        result.append('<a target="_blank" href="{url}">Download PDF</a>'.format(url=obj.pdf.url))
        return mark_safe(', '.join(result))

    def mark_as_paid(self, request, queryset):
        queryset.update(paid=True)

    def rollback(self, request, queryset):
        for report in queryset:
            if report.paid:
                messages.warning(request, 'Report {} was already paid.'.format(report.id))
                continue
            if report.cancelled:
                messages.warning(request, 'Report {} was already cancelled.'.format(report.id))
                continue

            report.rollback()
            messages.success(request, 'Report {} was rolled back successfully.'.format(report.id))

    def mark(self, request, queryset):
        for report in queryset:
            result = report.mark()
            messages.success(request, 'Report {} was marked successfully: {}'.format(report.id, result))

    def unmark(self, request, queryset):
        for report in queryset:
            result = report.unmark()
            messages.success(request, 'Report {} was unmarked successfully: {}'.format(report.id, result))

    def send_by_email(self, request, queryset):
        for report in queryset:
            report.send_by_email()


    rollback.short_description = 'DEBUG: Rollback old reports'

    mark.short_description = 'DEBUG: Mark all affected lead accounts'

    unmark.short_description = 'DEBUG: Unmark all affected lead accounts'
