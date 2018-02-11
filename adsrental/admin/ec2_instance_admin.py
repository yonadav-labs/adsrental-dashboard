from __future__ import unicode_literals

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.conf import settings

from adsrental.models.ec2_instance import EC2Instance
from adsrental.models.lead import Lead
from adsrental.admin.list_filters import LeadRaspberryPiOnlineListFilter, LeadRaspberryPiVersionListFilter


class EC2InstanceAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }

    model = EC2Instance
    list_display = (
        'id',
        'instance_id',
        'hostname',
        'version',
        'lead_link',
        'links',
        'raspberry_pi_link',
        'status',
        'last_troubleshoot',
        'tunnel_up',
    )
    list_filter = (
        'status',
        'tunnel_up',
        LeadRaspberryPiOnlineListFilter,
        LeadRaspberryPiVersionListFilter,
    )
    readonly_fields = ('created', 'updated', )
    search_fields = ('instance_id', 'email', 'rpid', 'lead__leadid', )
    list_select_related = ('lead', 'lead__raspberry_pi', )
    actions = (
        'update_ec2_tags',
        'get_currect_state',
        'check_missing',
        'restart',
        'start',
        'stop',
        'restart_raspberry_pi',
    )

    def lead_link(self, obj):
        if obj.lead is None:
            return obj.email
        return '<a target="_blank" href="{url}?q={q}">{lead} {status}</a>'.format(
            url=reverse('admin:adsrental_lead_changelist'),
            lead=obj.lead.email,
            status='(active)' if obj.lead.is_active() else '',
            q=obj.lead.email,
        )

    def raspberry_pi_link(self, obj):
        if obj.lead is None or obj.lead.raspberry_pi is None:
            return obj.rpid
        return '<a target="_blank" href="{url}?q={q}">{rpid} v. {version} {status}</a>'.format(
            url=reverse('admin:adsrental_raspberrypi_changelist'),
            rpid=obj.lead.raspberry_pi.rpid,
            version=obj.lead.raspberry_pi.version,
            status='(online)' if obj.lead.raspberry_pi.online() else '',
            q=obj.lead.raspberry_pi.rpid,
        )

    def links(self, obj):
        links = []
        if obj.lead and obj.lead.raspberry_pi:
            links.append('<a target="_blank" href="{url}">RDP</a>'.format(
                url=reverse('rdp', kwargs=dict(rpid=obj.rpid)),
            ))
            links.append('<a target="_blank" href="/log/{rpid}/{date}.log">Today log</a>'.format(
                rpid=obj.rpid,
                date=timezone.now().strftime(settings.LOG_DATE_FORMAT),
            ))

        links.append('<a href="#" title="ssh -i ~/.ssh/farmbot Administrator@{hostname} -p 40594">Copy SSH</a>'.format(
            hostname=obj.hostname,
        ))
        links.append('<a target="_blank" href="http://{hostname}:13608">Web</a>'.format(
            hostname=obj.hostname,
        ))
        return ', '.join(links)

    def update_ec2_tags(self, request, queryset):
        for ec2_instance in queryset:
            ec2_instance.set_ec2_tags()

    def get_currect_state(self, request, queryset):
        if queryset.count() > 10:
            queryset = EC2Instance.objects.all()

        for ec2_instance in queryset:
            ec2_instance.update_from_boto()

    def restart(self, request, queryset):
        for ec2_instance in queryset:
            ec2_instance.restart()

    def start(self, request, queryset):
        for ec2_instance in queryset:
            ec2_instance.start()

    def stop(self, request, queryset):
        for ec2_instance in queryset:
            ec2_instance.stop()

    def restart_raspberry_pi(self, request, queryset):
        for ec2_instance in queryset:
            if ec2_instance.lead and ec2_instance.lead.raspberry_pi:
                ec2_instance.lead.raspberry_pi.restart_required = True
                ec2_instance.lead.raspberry_pi.save()

    def check_missing(self, request, queryset):
        leads = Lead.objects.filter(
            ec2instance__isnull=True,
            raspberry_pi__isnull=False,
            status__in=[Lead.STATUS_QUALIFIED, Lead.STATUS_AVAILABLE, Lead.STATUS_IN_PROGRESS],
        )
        for lead in leads:
            EC2Instance.launch_for_lead(lead)

    lead_link.short_description = 'Lead'
    lead_link.allow_tags = True
    raspberry_pi_link.short_description = 'RaspberryPi'
    raspberry_pi_link.allow_tags = True
    links.allow_tags = True
