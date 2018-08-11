from django.contrib import admin
from django.urls import reverse
from django.utils import timezone, timesince
from django.utils.safestring import mark_safe

from adsrental.models.raspberry_pi_session import RaspberryPiSession


class RaspberryPiSessionAdmin(admin.ModelAdmin):
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

    def raspberry_pi_link(self, obj):
        result = []
        if obj.raspberry_pi:
            result.append('<a target="_blank" href="{url}?q={rpid}">{rpid}</a> (<a target="_blank" href="/log/{rpid}">Logs</a>, <a href="{rdp_url}">RDP</a>)'.format(
                rdp_url=reverse('rdp_ec2_connect', kwargs={'rpid': obj.raspberry_pi.rpid}),
                url=reverse('admin:adsrental_raspberrypi_changelist'),
                rpid=obj.raspberry_pi,
            ))

        return mark_safe('\n'.join(result))

    def duration(self, obj):
        end_date = obj.end_date or timezone.now()
        return timesince.timesince(obj.start_date, end_date)

    raspberry_pi_link.short_description = 'Raspberry Pi'
