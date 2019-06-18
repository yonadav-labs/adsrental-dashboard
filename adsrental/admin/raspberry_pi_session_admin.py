from django.contrib import admin
from django.urls import reverse
from django.utils import timezone, timesince
from django.utils.safestring import mark_safe

from adsrental.models.raspberry_pi_session import RaspberryPiSession
from adsrental.admin.base import CSVExporter


class RaspberryPiSessionAdmin(admin.ModelAdmin, CSVExporter):
    csv_fields = (
        'id',
        'raspberry_pi',
        'start_date',
        'end_date',
        'duration',
    )

    csv_titles = (
        'Id',
        'Raspberry PI',
        'Start Date',
        'End Date',
        'Duration',
    )

    model = RaspberryPiSession
    list_display = (
        'id',
        'raspberry_pi_link',
        'start_date',
        'end_date',
        'duration',
    )
    list_select_related = ('raspberry_pi', )
    search_fields = ('raspberry_pi__rpid', )
    raw_id_fields = ('raspberry_pi', )
    readonly_fields = ('start_date', )
    actions = ('export_as_csv',)

    def raspberry_pi_link(self, obj):
        result = []
        if obj.raspberry_pi:
            result.append('<a href="{url}?rpid={rpid}">{rpid}</a> (<a href="{log_url}">Logs</a>, <a href="{rdp_url}">RDP</a>)'.format(
                rdp_url=reverse('rdp_ec2_connect', kwargs={'rpid': obj.raspberry_pi.rpid}),
                url=reverse('admin:adsrental_raspberrypi_changelist'),
                log_url=reverse('show_log_dir', kwargs={'rpid': obj.raspberry_pi.rpid}),
                rpid=obj.raspberry_pi.rpid,
            ))

        return mark_safe('\n'.join(result))

    def duration(self, obj):
        end_date = obj.end_date or timezone.now()
        return timesince.timesince(obj.start_date, end_date)

    raspberry_pi_link.short_description = 'Raspberry Pi'
