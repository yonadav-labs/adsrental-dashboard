
from __future__ import unicode_literals

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import naturaltime

from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.admin.list_filters import OnlineListFilter, VersionListFilter


class RaspberryPiAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }

    model = RaspberryPi
    list_display = (
        'rpid',
        'lead_link',
        'ec2_instance_link',
        'version',
        'first_tested_field',
        'first_seen_field',
        'last_seen_field',
        'online',
    )
    search_fields = ('leadid', 'rpid', )
    list_filter = (
        OnlineListFilter,
        VersionListFilter,
    )
    list_select_related = ('lead', 'lead__ec2instance', )
    actions = (
        'restart_tunnel',
    )
    readonly_fields = ('created', 'updated', )

    def lead_link(self, obj):
        lead = obj.get_lead()
        if lead is None:
            return obj.leadid
        return '<a target="_blank" href="{url}?q={q}">{lead} {status}</a>'.format(
            url=reverse('admin:adsrental_lead_changelist'),
            lead=lead.email,
            status='(active)' if lead.is_active() else '',
            q=lead.leadid,
        )

    def ec2_instance_link(self, obj):
        ec2_instance = obj.get_ec2_instance()
        if not ec2_instance:
            return None
        result = []
        if ec2_instance:
            result.append('<a target="_blank" href="{url}?q={q}">{ec2_instance}</a>'.format(
                url=reverse('admin:adsrental_ec2instance_changelist'),
                ec2_instance=ec2_instance,
                q=ec2_instance.instance_id,
            ))

        return '\n'.join(result)

    def online(self, obj):
        return obj.online()

    def first_tested_field(self, obj):
        if not obj.first_tested:
            return '<img src="/static/admin/img/icon-no.svg" title="Never" alt="False">'

        return '<img src="/static/admin/img/icon-yes.svg" title="{}" alt="True">'.format(naturaltime(obj.first_tested))

    def first_seen_field(self, obj):
        if obj.first_seen is None:
            return None

        first_seen = obj.get_first_seen()
        return u'<span title="{}">{}</span>'.format(first_seen, naturaltime(first_seen))

    def last_seen_field(self, obj):
        if obj.last_seen is None:
            return None

        last_seen = obj.get_last_seen()

        return u'<span title="{}">{}</span>'.format(last_seen, naturaltime(last_seen))

    def restart_tunnel(self, request, queryset):
        for raspberry_pi in queryset:
            raspberry_pi.restart_required = True
            raspberry_pi.save()
        messages.info(request, 'Restart successfully requested. RPi and tunnel should be online in two minutes.')

    lead_link.short_description = 'Lead'
    lead_link.allow_tags = True
    ec2_instance_link.short_description = 'EC2 Instance'
    ec2_instance_link.allow_tags = True
    online.boolean = True
    first_tested_field.short_description = 'Tested'
    first_tested_field.allow_tags = True
    first_seen_field.short_description = 'First Seen'
    first_seen_field.empty_value_display = 'Never'
    first_seen_field.allow_tags = True
    last_seen_field.short_description = 'Last Seen'
    last_seen_field.empty_value_display = 'Never'
    last_seen_field.allow_tags = True
