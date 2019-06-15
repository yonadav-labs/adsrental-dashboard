from django.contrib import admin, messages
from django.urls import reverse
from django.utils.safestring import mark_safe

from adsrental.models.vultr_instance import VultrInstance
from adsrental.admin.base import CSVExporter


class VultrInstanceAdmin(admin.ModelAdmin, CSVExporter):
    csv_fields = (
        'id',
    )

    csv_titles = (
        'ID',
    )

    model = VultrInstance
    list_display = (
        'instance_id',
        'label',
        'ip_address',
        'os',
        'status',
        'links',
    )
    list_filter = (
        'tag',
    )
    actions = (
        'refresh',
        'export_as_csv',
    )
    search_fields = ('lead__email', 'lead__raspberry_pi__rpid', )

    def links(self, obj):
        links = []
        if obj.is_running():
            links.append('<a target="_blank" href="{url}">Connect</a>'.format(
                url=reverse('rdp_vultr_connect', kwargs=dict(vultr_instance_id=obj.id)),
            ))
        return mark_safe(', '.join(links))

    def refresh(self, request, queryset):
        if queryset.count() > 1:
            VultrInstance.update_all_from_vultr()
            messages.success(request, 'All instances updated from Vultr')
            return

        for vultr_instance in queryset:
            vultr_instance.update_from_vultr()
            messages.success(request, 'Instance {} updated from Vultr'.format(vultr_instance.label))
