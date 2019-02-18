from django.contrib import admin, messages
from django.urls import reverse
from django.utils.safestring import mark_safe

from adsrental.models.bundler_payments_report import BundlerPaymentsReport
from adsrental.models.bundler_payment import BundlerPayment


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
        'send_by_email',
        'discard_report',
    )

    def get_actions(self, request):
        actions = super(BundlerPaymentsReportAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def links(self, obj):
        result = []
        result.append('<a target="_blank" href="{url}">View</a>'.format(url=reverse('bundler_payments', kwargs=dict(report_id=obj.id))))
        result.append('<a target="_blank" href="{url}">Download PDF</a>'.format(url=obj.pdf.url))
        return mark_safe(', '.join(result))

    def mark_as_paid(self, request, queryset):
        queryset.update(paid=True)

    def discard_report(self, request, queryset):
        for report in queryset:
            BundlerPayment.objects.filter(report=report).update(report=None, paid=False)
            report.cancelled = True
            report.save()
            messages.success(request, f'Report for {report.date} has been disacarded')

    def send_by_email(self, request, queryset):
        for report in queryset:
            report.send_by_email()

    discard_report.short_description = 'DEBUG: Discard this report'
