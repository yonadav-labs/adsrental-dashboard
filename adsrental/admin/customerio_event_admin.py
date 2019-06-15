from django.contrib import admin

from adsrental.models.customerio_event import CustomerIOEvent
from adsrental.admin.base import CSVExporter


class CustomerIOEventAdmin(admin.ModelAdmin, CSVExporter):
    model = CustomerIOEvent
    csv_fields = (
        'id',
    )

    csv_titles = (
        'ID',
    )
    list_display = ('id', 'lead', 'lead_name', 'lead_email', 'name', 'sent', 'created')
    search_fields = ('lead__email', 'lead__first_name',
                     'lead__last_name', 'name', )
    list_filter = ('name', )
    readonly_fields = ('created', )
    actions = (
        'export_as_csv',
    )

    def lead_email(self, obj):
        return obj.lead.email

    def lead_name(self, obj):
        return obj.lead.name()
