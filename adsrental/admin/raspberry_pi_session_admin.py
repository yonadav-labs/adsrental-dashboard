from __future__ import unicode_literals

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils import timezone

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

    def raspberry_pi_link(self, obj):
        result = []
        if obj.raspberry_pi:
            result.append('<a target="_blank" href="{url}?q={rpid}">{rpid}</a> (<a target="_blank" href="/log/{rpid}">Logs</a>, <a href="{rdp_url}">RDP</a>, <a href="{config_url}">Config file</a>)'.format(
                rdp_url=reverse('rdp', kwargs={'rpid': obj.raspberry_pi}),
                url=reverse('admin:adsrental_raspberrypi_changelist'),
                config_url=reverse('farming_pi_config', kwargs={'rpid': obj.raspberry_pi}),
                rpid=obj.raspberry_pi,
            ))

    def duration(self, obj):
        end_date = obj.end_date or timezone.now()
        return '{} hours'.format(round((end_date - obj.start_date).total_seconds() / 3600., 1))

    raspberry_pi_link.short_description = 'Lead'
    raspberry_pi_link.allow_tags = True
