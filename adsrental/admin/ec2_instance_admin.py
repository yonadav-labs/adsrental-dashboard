from __future__ import unicode_literals

from django.contrib import admin, messages
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils.safestring import mark_safe

from adsrental.models.ec2_instance import EC2Instance
from adsrental.models.lead import Lead
from adsrental.admin.list_filters import LeadRaspberryPiOnlineListFilter, LeadRaspberryPiVersionListFilter, LeadStatusListFilter, LastTroubleshootListFilter, TunnelUpListFilter
from adsrental.utils import BotoResource


class EC2InstanceAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }

    model = EC2Instance
    list_display = (
        'id',
        'hostname',
        'instance_type',
        'lead_link',
        'lead_status',
        'raspberry_pi_link',
        'version',
        'raspberry_pi_version',
        'status',
        'last_rdp_session',
        'last_seen',
        'last_troubleshoot_field',
        'tunnel_up_date_field',
        'links',
        'raspberry_pi_online',
    )
    list_filter = (
        'status',
        'instance_type',
        TunnelUpListFilter,
        LeadStatusListFilter,
        LeadRaspberryPiOnlineListFilter,
        LeadRaspberryPiVersionListFilter,
        LastTroubleshootListFilter,
    )
    readonly_fields = ('created', 'updated', )
    search_fields = ('instance_id', 'email', 'rpid', 'lead__leadid', )
    list_select_related = ('lead', 'lead__raspberry_pi', )
    actions = (
        'update_ec2_tags',
        'get_currect_state',
        'check_missing',
        'start',
        'stop',
        'restart_raspberry_pi',
        'clear_ping_cache',
        'terminate',
        'update_password',
        'upgrade_to_xlarge',
    )
    raw_id_fields = ('lead', )

    def lead_link(self, obj):
        if obj.lead is None:
            return obj.email
        return mark_safe('<a target="_blank" href="{url}?q={q}">{lead}</a>'.format(
            url=reverse('admin:adsrental_lead_changelist'),
            lead=obj.lead.email,
            q=obj.lead.email,
        ))

    def lead_status(self, obj):
        return obj.lead and obj.lead.status

    def raspberry_pi_link(self, obj):
        if obj.lead is None or obj.lead.raspberry_pi is None:
            return obj.rpid
        return mark_safe('<a target="_blank" href="{url}?q={q}">{rpid}</a>'.format(
            url=reverse('admin:adsrental_raspberrypi_changelist'),
            rpid=obj.lead.raspberry_pi.rpid,
            q=obj.lead.raspberry_pi.rpid,
        ))

    def raspberry_pi_online(self, obj):
        return obj.lead and obj.lead.raspberry_pi and obj.lead.raspberry_pi.online()

    def raspberry_pi_version(self, obj):
        return obj.lead and obj.lead.raspberry_pi and obj.lead.raspberry_pi.version

    def last_seen(self, obj):
        if obj.lead is None or obj.lead.raspberry_pi is None or obj.lead.raspberry_pi.last_seen is None:
            return None

        date = obj.lead.raspberry_pi.last_seen
        return mark_safe(u'<span title="{}">{}</span>'.format(date, naturaltime(date)))

    def last_rdp_session(self, obj):
        if not obj.last_rdp_start:
            return None

        date = obj.last_rdp_start
        return mark_safe(u'<span title="{}">{}</span>'.format(date, naturaltime(date)))

    def last_troubleshoot_field(self, obj):
        if obj.last_troubleshoot is None:
            return 'Never'

        date = obj.last_troubleshoot
        return mark_safe(u'<span title="{}">{}</span>'.format(date, naturaltime(date)))

    def tunnel_up_date_field(self, obj):
        if obj.tunnel_up_date is None:
            return 'Never'

        date = obj.tunnel_up_date
        is_tunnel_up = obj.is_tunnel_up()
        return mark_safe(u'<span title="{}">{}</span>'.format(
            date,
            'Yes' if is_tunnel_up else naturaltime(date),
        ))

    def links(self, obj):
        links = []
        if obj.rpid:
            links.append('<a target="_blank" href="{url}?rpid={rpid}">RDP</a>'.format(
                url=reverse('rdp_connect'),
                rpid=obj.rpid,
            ))
        if obj.lead and obj.lead.raspberry_pi:
            today_log_filename = '{}.log'.format(timezone.now().strftime(settings.LOG_DATE_FORMAT))
            links.append('<a target="_blank" href="{log_url}">Today log</a>'.format(
                log_url=reverse('show_log', kwargs={'rpid': obj.rpid, 'filename': today_log_filename}),
            ))
            links.append('<a target="_blank" href="{url}">Netstat</a>'.format(
                url=reverse('ec2_ssh_get_netstat', kwargs=dict(rpid=obj.rpid)),
            ))
            links.append('<a target="_blank" href="{url}">RTunnel</a>'.format(
                url=reverse('ec2_ssh_start_reverse_tunnel', kwargs=dict(rpid=obj.rpid)),
            ))

        links.append('<a href="#" title="ssh -o StrictHostKeyChecking=no -i ~/.ssh/farmbot Administrator@{hostname} -p 40594">Copy SSH</a>'.format(
            hostname=obj.hostname,
        ))
        return mark_safe(', '.join(links))

    def update_ec2_tags(self, request, queryset):
        for ec2_instance in queryset:
            ec2_instance.set_ec2_tags()

    def get_currect_state(self, request, queryset):
        if queryset.count() > 10:
            boto_resource = BotoResource()
            for ec2_boto in boto_resource.get_resource('ec2').instances.all():
                ec2 = EC2Instance.objects.filter(instance_id=ec2_boto.id).first()
                if ec2:
                    ec2.update_from_boto(ec2_boto)

        for ec2_instance in queryset:
            ec2_instance.update_from_boto()

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
                ec2_instance.clear_ping_cache()

    def check_missing(self, request, queryset):
        leads = Lead.objects.filter(
            ec2instance__isnull=True,
            raspberry_pi__isnull=False,
            status__in=[Lead.STATUS_QUALIFIED, Lead.STATUS_AVAILABLE, Lead.STATUS_IN_PROGRESS],
        )
        for lead in leads:
            EC2Instance.launch_for_lead(lead)

    def clear_ping_cache(self, request, queryset):
        for ec2_instance in queryset:
            ec2_instance.clear_ping_cache()

    def terminate(self, request, queryset):
        for ec2_instance in queryset:
            ec2_instance.terminate()

    def update_password(self, request, queryset):
        for ec2_instance in queryset:
            ec2_instance.change_password()

    def upgrade_to_xlarge(self, request, queryset):
        client = BotoResource().get_client('ec2')
        for ec2_instance in queryset:
            if ec2_instance.instance_type == EC2Instance.INSTANCE_TYPE_XLARGE:
                messages.warning(request, 'EC2 was already upgraded')
                continue
            ec2_instance.update_from_boto()
            if ec2_instance.status != EC2Instance.STATUS_STOPPED:
                messages.success(request, 'EC2 should be stopped first')
                continue

            client.modify_instance_attribute(InstanceId=ec2_instance.instance_id, Attribute='instanceType', Value=EC2Instance.INSTANCE_TYPE_XLARGE)
            ec2_instance.instance_type = EC2Instance.INSTANCE_TYPE_XLARGE
            ec2_instance.save()
            messages.success(request, 'EC2 is upgraded successfully')

    lead_link.short_description = 'Lead'

    raspberry_pi_link.short_description = 'RaspberryPi'

    raspberry_pi_version.short_description = 'RPi Version'

    raspberry_pi_online.boolean = True
    raspberry_pi_online.short_description = 'RPi Online'

    last_troubleshoot_field.short_description = 'Troubleshoot'
    last_troubleshoot_field.admin_order_field = 'last_troubleshoot'

    tunnel_up_date_field.short_description = 'Tunnel up'
    tunnel_up_date_field.admin_order_field = 'tunnel_up_date'

    last_seen.admin_order_field = 'lead__raspberry_pi__last_seen'

    clear_ping_cache.short_description = 'DEBUG: Clear ping cache'

    terminate.short_description = 'DEBUG: Terminate'

    upgrade_to_xlarge.short_description = 'DEBUG: Upgrade to T2 Xlarge instance'
