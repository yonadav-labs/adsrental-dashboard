from __future__ import unicode_literals

from django.contrib import admin

from adsrental.models.customerio_event import CustomerIOEvent


class CustomerIOEventAdmin(admin.ModelAdmin):
    model = CustomerIOEvent
    list_display = ('id', 'lead', 'lead_name', 'lead_email', 'name', 'sent', 'created')
    search_fields = ('lead__email', 'lead__first_name',
                     'lead__last_name', 'name', )
    list_filter = ('name', )
    readonly_fields = ('created', )

    def lead_email(self, obj):
        return obj.lead.email

    def lead_name(self, obj):
        return obj.lead.name()
