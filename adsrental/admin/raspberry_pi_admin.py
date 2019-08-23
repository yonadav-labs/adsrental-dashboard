from django.contrib import admin
from django.urls import reverse
from django.conf import settings
from django.utils import timezone, timesince
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils.safestring import mark_safe
from django.db.models import Value
from django.db.models.functions import Concat

from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.models.ec2_instance import EC2Instance
from adsrental.admin.list_filters import OnlineListFilter, VersionListFilter, AbstractUIDListFilter, ProxyDelayFilter
from adsrental.admin.base import CSVExporter


PROXY_TUNNEL_MESSAGE = '''Your device should be updated in a couple of minutes!<br />
1) Create a new profile in MultiloginApp, name it <b>{rpid} {lead_name}</b>, if it does not exist yet.<br />
2) Go to Edit, proxy settings<br />
3) select <b>Socks 5 proxy</b> connection type<br />
4) Set Address to <b>{host}</b><br />
5) Set Port to <b>{rtunnel_port}</b><br />
6) Set Login to <b>{user}</b><br />
7) Set Password to <b>{password}</b><br />
8) Save and launch your new profile.<br />
9) Ping @vlad if something is not working.<br />'''


class RpidListFilter(AbstractUIDListFilter):
    parameter_name = 'rpid'
    title = 'RPID'


class RaspberryPiAdmin(admin.ModelAdmin, CSVExporter):
    csv_fields = (
        'rpid',
        'lead',
        'lead__status',
        'version',
        'ip_address',
        'first_tested',
        'first_seen',
        'last_seen',
        'days_online',
        'days_offline',
        'online',
        'uptime',
        'is_proxy_tunnel',
        'created'
    )

    csv_titles = (
        'Rpid',
        'Lead',
        'Lead Status',
        'Version',
        'Ip Address',
        'First Tested',
        'First Seen',
        'Last Seen',
        'Days Online',
        'Days Offline',
        'Online',
        'Uptime',
        'Is Proxy Tunnel',
        'Created'
    )

    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }

    change_list_template = 'admin/custom_change_list.html'
    model = RaspberryPi
    list_display = (
        'rpid',
        'lead_link',
        'lead_status',
        # 'ec2_instance_link',
        'version',
        'ip_address',
        'first_tested_field',
        'first_seen_field',
        'last_seen_field',
        'links',
        'online',
        'uptime',
        'is_proxy_tunnel',
        # 'proxy_hostname',
        # 'rtunnel_port',
        # 'tunnel_online',
        # 'new_config_required',
    )
    search_fields = ('leadid', 'rpid', )
    list_filter = (
        OnlineListFilter,
        VersionListFilter,
        RpidListFilter,
        ProxyDelayFilter,
        'proxy_hostname'
        'proxy_delay'
        'is_proxy_tunnel',
        'proxy_hostname',
    )
    list_select_related = ('lead', 'lead__ec2instance', )
    actions = (
        'restart_device',
        'update_config',
        'reset_cache',
        'show_cache',
        'convert_to_proxy_tunnel',
        'convert_to_ec2',
        'export_as_csv',
    )
    readonly_fields = ('created', 'updated', )

    def lead_link(self, obj):
        lead = obj.get_lead()
        if lead is None:
            return obj.leadid
        return mark_safe('<a href="{url}?leadid={q}">{lead}</a>'.format(
            url=reverse('admin:adsrental_lead_changelist'),
            lead=lead.email,
            q=lead.leadid,
        ))

    def lead_status(self, obj):
        return obj.lead and obj.lead.status

    def days_online(self, obj):
        if obj.online_since_date:
            now = timezone.now()
            return int((now - obj.online_since_date).total_seconds() / 3600 / 24)

    def days_offline(self, obj):
        if obj.last_seen:
            now = timezone.now()
            return int((now - obj.last_seen).total_seconds() / 3600 / 24)

    def ec2_instance_link(self, obj):
        ec2_instance = obj.get_ec2_instance()
        if not ec2_instance:
            return None
        result = []
        if ec2_instance:
            result.append('<a href="{url}?q={q}">{ec2_instance}</a>'.format(
                url=reverse('admin:adsrental_ec2instance_changelist'),
                ec2_instance=ec2_instance,
                q=ec2_instance.instance_id,
            ))

        return mark_safe('\n'.join(result))

    def online(self, obj):
        return obj.online()

    def uptime(self, obj):
        if not obj.online():
            return None

        return timesince.timesince(obj.online_since_date)

    def tunnel_online(self, obj):
        ec2_instance = obj.get_ec2_instance()
        if not ec2_instance:
            return None

        return ec2_instance.is_tunnel_up()

    def first_tested_field(self, obj):
        if not obj.first_tested:
            return mark_safe('<img src="/static/admin/img/icon-no.svg" title="Never" alt="False">')

        return mark_safe('<img src="/static/admin/img/icon-yes.svg" title="{}" alt="True">'.format(naturaltime(obj.first_tested)))

    def first_seen_field(self, obj):
        if obj.first_seen is None:
            return None

        first_seen = obj.get_first_seen()
        return mark_safe(u'<span title="{}">{}</span>'.format(first_seen, naturaltime(first_seen)))

    def last_seen_field(self, obj):
        last_seen = obj.get_last_seen()
        if not last_seen:
            return None
        return mark_safe(u'<span title="{}">{}</span>'.format(last_seen, naturaltime(last_seen)))

    def restart_device(self, request, queryset):
        for raspberry_pi in queryset:
            raspberry_pi.reset_cache()
            raspberry_pi.restart_required = True
            raspberry_pi.save()
            messages.success(request, f'Restart successfully requested for {raspberry_pi.rpid}. RPi and tunnel should be online in two minutes.')

    def update_config(self, request, queryset):
        for raspberry_pi in queryset:
            raspberry_pi.reset_cache()
            raspberry_pi.new_config_required = True
            raspberry_pi.save()
            messages.success(request, f'New config successfully requested for {raspberry_pi.rpid}. Tunnel should be online in two minutes.')

    def convert_to_ec2(self, request, queryset):
        for raspberry_pi in queryset:
            raspberry_pi.reset_cache()
            raspberry_pi.is_proxy_tunnel = False
            raspberry_pi.new_config_required = True
            raspberry_pi.unassign_tunnel_ports()
            raspberry_pi.save()

            lead = raspberry_pi.get_lead()
            ec2_instance = raspberry_pi.get_ec2_instance()
            if ec2_instance:
                ec2_instance.start()
            else:
                EC2Instance.launch_for_lead(lead)

            messages.success(request, f'Device {raspberry_pi.rpid} converted to EC2')

    def convert_to_proxy_tunnel(self, request, queryset):
        for raspberry_pi in queryset:
            raspberry_pi.reset_cache()
            raspberry_pi.is_proxy_tunnel = True
            raspberry_pi.new_config_required = True
            raspberry_pi.assign_proxy_hostname()
            raspberry_pi.assign_tunnel_ports()
            raspberry_pi.save()

            ec2_instance = raspberry_pi.get_ec2_instance()
            if ec2_instance:
                ec2_instance.unassign_essential()
                ec2_instance.stop()
                messages.info(request, 'Unassigned EC2.')

            messages.success(request, PROXY_TUNNEL_MESSAGE.format(
                rpid=raspberry_pi.rpid,
                lead_name=raspberry_pi.get_lead().name() if raspberry_pi.get_lead() else '',
                rtunnel_port=raspberry_pi.rtunnel_port,
                host=raspberry_pi.TUNNEL_HOST,
                user=raspberry_pi.TUNNEL_USER,
                password=raspberry_pi.TUNNEL_PASSWORD,
            ), extra_tags='safe')

    def reset_cache(self, request, queryset):
        for raspberry_pi in queryset:
            raspberry_pi.reset_cache()
            raspberry_pi.save()
            messages.success(request, f'Cache reset successful for {raspberry_pi.rpid}.')

    def show_cache(self, request, queryset):
        for raspberry_pi in queryset:
            cache_data = raspberry_pi.get_cache()
            messages.info(request, f'{raspberry_pi.rpid} cache: {cache_data}')

    def links(self, obj):
        links = []
        now = timezone.localtime(timezone.now())
        if obj.is_proxy_tunnel:
            links.append('<a href="{url}">Proxy tunnel</a>'.format(
                url=reverse('rpi_proxy_tunnel_info', kwargs=dict(rpid=obj.rpid)),
            ))
        else:
            links.append('<a href="{url}">RDP</a>'.format(
                url=reverse('rdp_ec2_connect', kwargs=dict(rpid=obj.rpid)),
            ))
        links.append('<a href="{url}">pi.conf</a>'.format(
            url=reverse('pi_config', kwargs=dict(rpid=obj.rpid)),
        ))
        today_log_filename = '{}.log'.format(now.strftime(settings.LOG_DATE_FORMAT))
        links.append('<a href="{log_url}">Today log</a>'.format(
            log_url=reverse('show_log', kwargs={'rpid': obj.rpid, 'filename': today_log_filename}),
        ))
        links.append('<a href="{url}?q={rpid}">Sessions</a>'.format(
            url=reverse('admin:adsrental_raspberrypisession_changelist'),
            rpid=obj.rpid,
        ))

        return mark_safe(', '.join(links))

    lead_link.short_description = 'Lead'
    lead_link.admin_order_field = Concat('lead__first_name', Value(' '), 'lead__last_name')

    ec2_instance_link.short_description = 'EC2 Instance'

    online.boolean = True

    tunnel_online.boolean = True

    first_tested_field.short_description = 'Tested'
    first_tested_field.admin_order_field = 'first_tested'

    first_seen_field.short_description = 'First Seen'
    first_seen_field.empty_value_display = 'Never'
    first_seen_field.admin_order_field = 'first_seen'

    last_seen_field.short_description = 'Last Seen'
    last_seen_field.empty_value_display = 'Never'
    last_seen_field.admin_order_field = 'last_seen'

    uptime.admin_order_field = 'online_since_date'
