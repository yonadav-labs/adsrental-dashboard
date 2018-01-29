from __future__ import unicode_literals

import datetime

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils import timezone
from django.contrib.admin import SimpleListFilter
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.conf import settings

from adsrental.models import User, Lead, RaspberryPi, CustomerIOEvent, EC2Instance
from salesforce_handler.models import Lead as SFLead
from salesforce_handler.models import RaspberryPi as SFRaspberryPi
from adsrental.utils import ShipStationClient


class OnlineListFilter(SimpleListFilter):
    title = 'EC2 online state'
    parameter_name = 'online'

    def lookups(self, request, model_admin):
        return (
            ('online', 'Online only'),
            ('offline', 'Offline only'),
            ('offline_2days', 'Offline for last 2 days'),
            ('offline_5days', 'Offline for last 5 days'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'online':
            return queryset.filter(raspberry_pi__last_seen__gt=timezone.now() - datetime.timedelta(hours=14))
        if self.value() == 'offline':
            return queryset.filter(raspberry_pi__last_seen__lte=timezone.now() - datetime.timedelta(hours=14))
        if self.value() == 'offline_2days':
            return queryset.filter(raspberry_pi__last_seen__lte=timezone.now() - datetime.timedelta(hours=14 + 2 * 24))
        if self.value() == 'offline_5days':
            return queryset.filter(raspberry_pi__last_seen__lte=timezone.now() - datetime.timedelta(hours=14 + 5 * 24))


class RaspberryPiOnlineListFilter(SimpleListFilter):
    title = 'EC2 online state'
    parameter_name = 'online'

    def lookups(self, request, model_admin):
        return (
            ('online', 'Online only'),
            ('offline', 'Offline only'),
            ('offline_2days', 'Offline for last 2 days'),
            ('offline_5days', 'Offline for last 5 days'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'online':
            return queryset.filter(last_seen__gt=timezone.now() - datetime.timedelta(hours=14))
        if self.value() == 'offline':
            return queryset.filter(last_seen__lte=timezone.now() - datetime.timedelta(hours=14))
        if self.value() == 'offline_2days':
            return queryset.filter(last_seen__lte=timezone.now() - datetime.timedelta(hours=14 + 2 * 24))
        if self.value() == 'offline_5days':
            return queryset.filter(last_seen__lte=timezone.now() - datetime.timedelta(hours=14 + 5 * 24))


class TunnelOnlineListFilter(SimpleListFilter):
    title = 'Tunnel online state'
    parameter_name = 'tunnel_online'

    def lookups(self, request, model_admin):
        return (
            ('online', 'Online only'),
            ('offline', 'Offline only'),
            ('offline_2days', 'Offline for last 2 days'),
            ('offline_5days', 'Offline for last 5 days'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'online':
            return queryset.filter(raspberry_pi__tunnel_last_tested__gt=timezone.now() - datetime.timedelta(hours=14))
        if self.value() == 'offline':
            return queryset.filter(raspberry_pi__tunnel_last_tested__lte=timezone.now() - datetime.timedelta(hours=14))
        if self.value() == 'offline_2days':
            return queryset.filter(raspberry_pi__tunnel_last_tested__lte=timezone.now() - datetime.timedelta(hours=14 + 2 * 24))
        if self.value() == 'offline_5days':
            return queryset.filter(raspberry_pi__tunnel_last_tested__lte=timezone.now() - datetime.timedelta(hours=14 + 5 * 24))


class AccountTypeListFilter(SimpleListFilter):
    title = 'Account type'
    parameter_name = 'account_type'

    def lookups(self, request, model_admin):
        return (
            ('facebook', 'Facebook'),
            ('google', 'Google'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'facebook':
            return queryset.filter(facebook_account=True)
        if self.value() == 'google':
            return queryset.filter(google_account=True)


class RaspberryPiTunnelOnlineListFilter(SimpleListFilter):
    title = 'Tunnel online state'
    parameter_name = 'tunnel_online'

    def lookups(self, request, model_admin):
        return (
            ('online', 'Online only'),
            ('offline', 'Offline only'),
            ('offline_2days', 'Offline for last 2 days'),
            ('offline_5days', 'Offline for last 5 days'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'online':
            return queryset.filter(tunnel_last_tested__gt=timezone.now() - datetime.timedelta(hours=14))
        if self.value() == 'offline':
            return queryset.filter(tunnel_last_tested__lte=timezone.now() - datetime.timedelta(hours=14))
        if self.value() == 'offline_2days':
            return queryset.filter(tunnel_last_tested__lte=timezone.now() - datetime.timedelta(hours=14 + 2 * 24))
        if self.value() == 'offline_5days':
            return queryset.filter(tunnel_last_tested__lte=timezone.now() - datetime.timedelta(hours=14 + 5 * 24))


class WrongPasswordListFilter(SimpleListFilter):
    title = 'Wrong Password'
    parameter_name = 'wrong_password'

    def lookups(self, request, model_admin):
        return (
            ('no', 'No'),
            ('yes', 'Yes'),
            ('yes_2days', 'Yes for 2 days'),
            ('yes_5days', 'Yes for 5 days'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'no':
            return queryset.filter(wrong_password=False)
        if self.value() == 'yes':
            return queryset.filter(wrong_password=True)
        if self.value() == 'yes_2days':
            return queryset.filter(wrong_password=True, raspberry_pi__last_seen__lte=timezone.now() - datetime.timedelta(hours=14 + 2 * 24))
        if self.value() == 'yes_5days':
            return queryset.filter(wrong_password=True, raspberry_pi__last_seen__lte=timezone.now() - datetime.timedelta(hours=14 + 5 * 24))


class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets[:-1] + (
        (
            None,
            {
                'fields': [
                    'utm_source',
                ],
            },
        ),
    )


class LeadAdmin(admin.ModelAdmin):
    model = Lead
    list_display = (
        'leadid',
        # 'usps_tracking_code',
        'account_name',
        'name',
        'status',
        'email_field',
        'phone',
        'google_account_column',
        'facebook_account_column',
        'raspberry_pi_link',
        'ec2_instance_link',
        'first_seen',
        'last_seen',
        'tunnel_last_tested',
        'online',
        'tunnel_online',
        'wrong_password',
        'pi_delivered',
        'bundler_paid',
        'tested',
    )
    list_filter = ('status', OnlineListFilter, TunnelOnlineListFilter, AccountTypeListFilter,
                   WrongPasswordListFilter, 'utm_source', 'bundler_paid', 'pi_delivered', 'tested', )
    select_related = ('raspberry_pi', 'ec2instance')
    search_fields = ('leadid', 'account_name', 'first_name',
                     'last_name', 'raspberry_pi__rpid', 'email', )
    actions = (
        'update_from_salesforce',
        'update_salesforce',
        'update_from_shipstation',
        'update_pi_delivered',
        'create_shipstation_order',
        'start_ec2',
        'restart_ec2',
        'troubleshoot_ec2',
        'show_errors',
        'restart_raspberry_pi',
        'force_update_raspberry_pi',
        'ban',
        'unban',
    )
    readonly_fields = ('created', 'updated', )

    def name(self, obj):
        return u'{} {}'.format(
            obj.first_name,
            obj.last_name,
        )

    def email_field(self, obj):
        return '{} (<a href="{}?q={}" target="_blank">SF</a>)'.format(
            obj.email,
            reverse('admin:salesforce_handler_lead_changelist'),
            obj.email,
        )

    def online(self, obj):
        return obj.raspberry_pi.online() if obj.raspberry_pi else False

    def tunnel_online(self, obj):
        return obj.raspberry_pi.tunnel_online() if obj.raspberry_pi else False

    def first_seen(self, obj):
        if obj.raspberry_pi is None or obj.raspberry_pi.first_seen is None:
            return None

        first_seen = obj.raspberry_pi.get_first_seen()
        return u'<span title="{}">{}</span>'.format(first_seen, naturaltime(first_seen))

    def last_seen(self, obj):
        if obj.raspberry_pi is None or obj.raspberry_pi.last_seen is None:
            return None

        last_seen = obj.raspberry_pi.get_last_seen()

        return u'<span title="{}">{}</span>'.format(last_seen, naturaltime(last_seen))

    def tunnel_last_tested(self, obj):
        if obj.raspberry_pi is None or obj.raspberry_pi.tunnel_last_tested is None:
            return None

        tunnel_last_tested = obj.raspberry_pi.get_tunnel_last_tested()
        return u'<span title="{}">{}</span>'.format(tunnel_last_tested, naturaltime(tunnel_last_tested))

    def facebook_account_column(self, obj):
        return '{} {}'.format(
            '<img src="/static/admin/img/icon-yes.svg" alt="True">' if obj.facebook_account else '<img src="/static/admin/img/icon-no.svg" alt="False">',
            obj.facebook_account_status,
        )

    def google_account_column(self, obj):
        return '{} {}'.format(
            '<img src="/static/admin/img/icon-yes.svg" alt="True">' if obj.google_account else '<img src="/static/admin/img/icon-no.svg" alt="False">',
            obj.google_account_status,
        )

    def raspberry_pi_link(self, obj):
        if obj.raspberry_pi is None:
            return None
        return '<a target="_blank" href="{url}?q={rpid}">{rpid}</a> (<a target="_blank" href="/log/{rpid}">Logs</a>, <a href="{rdp_url}">RDP</a>, <a href="{config_url}">Config file</a>)'.format(
            rdp_url=reverse('rdp', kwargs={'rpid': obj.raspberry_pi}),
            url=reverse('admin:adsrental_raspberrypi_changelist'),
            config_url=reverse('farming_pi_config', kwargs={'rpid': obj.raspberry_pi}),
            rpid=obj.raspberry_pi,
        )

    def ec2_instance_link(self, obj):
        if obj.ec2instance is None:
            return None
        return '<a target="_blank" href="{url}?q={q}">{ec2_instance}</a>'.format(
            url=reverse('admin:adsrental_ec2instance_changelist'),
            ec2_instance=obj.ec2instance,
            q=obj.ec2instance.instance_id,
        )

    def update_from_salesforce(self, request, queryset):
        sf_lead_ids = []
        leads_map = {}
        for lead in queryset:
            leads_map[lead.leadid] = lead
            sf_lead_ids.append(lead.leadid)

        sf_leads = SFLead.objects.filter(
            id__in=sf_lead_ids).simple_select_related('raspberry_pi')
        for sf_lead in sf_leads:
            Lead.upsert_from_sf(sf_lead, leads_map.get(sf_lead.id))

    def update_salesforce(self, request, queryset):
        sf_lead_ids = []
        leads_map = {}
        for lead in queryset:
            leads_map[lead.leadid] = lead
            sf_lead_ids.append(lead.leadid)

        sf_leads = SFLead.objects.filter(
            id__in=sf_lead_ids).simple_select_related('raspberry_pi')
        for sf_lead in sf_leads:
            Lead.upsert_to_sf(sf_lead, leads_map.get(sf_lead.id))

    def update_from_shipstation(self, request, queryset):
        for lead in queryset:
            lead.update_from_shipstation()

    def update_pi_delivered(self, request, queryset):
        for lead in queryset:
            lead.update_pi_delivered()

    def create_shipstation_order(self, request, queryset):
        for lead in queryset:
            if not lead.raspberry_pi:
                lead.raspberry_pi = RaspberryPi.objects.filter(lead__isnull=True, rpid__startswith='RP').first()
                lead.save()
                messages.success(
                    request, 'Lead {} has new Raspberry Pi assigned: {}'.format(lead.email, lead.raspberry_pi.rpid))

            sf_raspberry_pi = SFRaspberryPi.objects.filter(name=lead.raspberry_pi.rpid).first()
            RaspberryPi.upsert_to_sf(sf_raspberry_pi, lead.raspberry_pi)
            sf_lead = SFLead.objects.filter(email=lead.email).first()
            Lead.upsert_to_sf(sf_lead, lead)
            sf_lead = SFLead.objects.filter(email=lead.email).first()

            EC2Instance.launch_for_lead(lead)

            shipstation_client = ShipStationClient()
            if shipstation_client.get_sf_lead_order_data(sf_lead):
                messages.info(
                    request, 'Lead {} order already exists'.format(lead.email))
                continue

            order = shipstation_client.add_sf_lead_order(sf_lead)
            messages.success(
                request, '{} order created: {}'.format(lead.str(), order.order_key))

    def start_ec2(self, request, queryset):
        for lead in queryset:
            EC2Instance.launch_for_lead(self)

    def restart_ec2(self, request, queryset):
        for lead in queryset:
            lead.ec2instance.restart()

    def troubleshoot_ec2(self, request, queryset):
        for lead in queryset:
            ec2_instance = lead.get_ec2_instance()
            if ec2_instance:
                ec2_instance.troubleshoot()

    def show_errors(self, request, queryset):
        for lead in queryset:
            errors = lead.find_errors()
            if errors:
                for error in errors:
                    messages.error(request, 'Lead {}: {}'.format(lead.name(), error))
            else:
                messages.success(request, 'Lead {}: doing great'.format(lead.name()))

    def restart_raspberry_pi(self, request, queryset):
        for lead in queryset:
            lead.raspberry_pi.restart_required = True
            lead.raspberry_pi.save()
        messages.info(request, 'Lead {} RPi restart successfully requested. RPi and tunnel should be online in two minutes.'.format(lead.email))

    def force_update_raspberry_pi(self, request, queryset):
        for lead in queryset:
            raspberry_pi = lead.raspberry_pi
            cmd_to_execute = '''ssh pi@localhost -p 2046 "curl https://adsrental.com/static/update_pi.sh | bash"'''
            lead.ec2instance.ssh_execute(cmd_to_execute)
            raspberry_pi.version = settings.RASPBERRY_PI_VERSION
            raspberry_pi.save()

    def ban(self, request, queryset):
        for lead in queryset:
            lead.status = Lead.STATUS_BANNED
            lead.ec2instance = None
            lead.save()
            messages.info(request, 'Lead {} is banned.'.format(lead.email))

    def unban(self, request, queryset):
        for lead in queryset:
            lead.status = Lead.STATUS_QUALIFIED
            lead.save()
            EC2Instance.launch_for_lead(lead)
            messages.info(request, 'Lead {} is unbanned.'.format(lead.email))

    create_shipstation_order.short_description = 'Assign free RPi and create Shipstation order'
    ec2_instance_link.short_description = 'EC2 instance'
    ec2_instance_link.allow_tags = True
    start_ec2.short_description = 'Start EC2 instance'
    restart_ec2.short_description = 'Restart EC2 instance'
    email_field.allow_tags = True
    email_field.short_description = 'Email'
    email_field.admin_order_field = 'email'
    online.boolean = True
    online.admin_order_field = 'raspberry_pi__first_seen'
    tunnel_online.boolean = True
    tunnel_online.admin_order_field = 'raspberry_pi__tunnel_last_tested'
    raspberry_pi_link.short_description = 'Raspberry PI'
    raspberry_pi_link.allow_tags = True
    first_seen.empty_value_display = 'Never'
    first_seen.admin_order_field = 'raspberry_pi__first_seen'
    first_seen.allow_tags = True
    last_seen.empty_value_display = 'Never'
    last_seen.admin_order_field = 'raspberry_pi__last_seen'
    last_seen.allow_tags = True
    tunnel_last_tested.empty_value_display = 'Never'
    tunnel_last_tested.admin_order_field = 'raspberry_pi__tunnel_last_tested'
    tunnel_last_tested.allow_tags = True
    facebook_account_column.short_description = 'Facebook Account'
    facebook_account_column.allow_tags = True
    google_account_column.admin_order_field = 'facebook_account'
    google_account_column.short_description = 'Google Account'
    google_account_column.allow_tags = True
    google_account_column.admin_order_field = 'google_account'


class RaspberryPiAdmin(admin.ModelAdmin):
    model = RaspberryPi
    list_display = ('rpid', 'leadid', 'ipaddress', 'ec2_hostname', 'first_seen',
                    'last_seen', 'tunnel_last_tested', 'online', 'tunnel_online', )
    search_fields = ('leadid', 'rpid', 'ec2_hostname', 'ipaddress', )
    list_filter = (RaspberryPiOnlineListFilter,
                   RaspberryPiTunnelOnlineListFilter, )
    actions = (
        'update_from_salesforce',
        'update_to_salesforce',
        'restart_tunnel',
    )
    readonly_fields = ('created', 'updated', )

    def online(self, obj):
        return obj.online()

    def tunnel_online(self, obj):
        return obj.tunnel_online()

    def first_seen(self, obj):
        if obj.first_seen is None:
            return None

        return naturaltime(obj.raspberry_pi.get_first_seen())

    def last_seen(self, obj):
        if obj.last_seen is None:
            return None

        return obj.last_seen + ' ' + timezone.now()

        return naturaltime(obj.raspberry_pi.get_last_seen())

    def tunnel_last_tested(self, obj):
        if obj.tunnel_last_tested is None:
            return None

        return naturaltime(obj.get_tunnel_last_tested())

    def update_from_salesforce(self, request, queryset):
        sf_raspberry_pi_names = []
        raspberry_pis_map = {}
        for raspberry_pi in queryset:
            raspberry_pis_map[raspberry_pi.rpid] = raspberry_pi
            sf_raspberry_pi_names.append(raspberry_pi.rpid)

        sf_raspberry_pis = SFRaspberryPi.objects.filter(
            name__in=sf_raspberry_pi_names)

        for sf_raspberry_pi in sf_raspberry_pis:
            RaspberryPi.upsert_from_sf(
                sf_raspberry_pi, raspberry_pis_map.get(sf_raspberry_pi.name))

    def update_to_salesforce(self, request, queryset):
        sf_raspberry_pi_names = []
        raspberry_pis_map = {}
        for raspberry_pi in queryset:
            raspberry_pis_map[raspberry_pi.rpid] = raspberry_pi
            sf_raspberry_pi_names.append(raspberry_pi.rpid)

        sf_raspberry_pis = SFRaspberryPi.objects.filter(
            name__in=sf_raspberry_pi_names)

        for sf_raspberry_pi in sf_raspberry_pis:
            RaspberryPi.upsert_to_sf(
                sf_raspberry_pi, raspberry_pis_map.get(sf_raspberry_pi.name))

    def restart_tunnel(self, request, queryset):
        for raspberry_pi in queryset:
            raspberry_pi.restart_required = True
            raspberry_pi.save()
        messages.info(request, 'Restart successfully requested. RPi and tunnel should be online in two minutes.')

    online.boolean = True
    tunnel_online.boolean = True
    first_seen.empty_value_display = 'Never'
    last_seen.empty_value_display = 'Never'
    tunnel_last_tested.empty_value_display = 'Never'


class CustomerIOEventAdmin(admin.ModelAdmin):
    model = CustomerIOEvent
    list_display = ('id', 'lead', 'lead_name', 'lead_email', 'name', 'created')
    search_fields = ('lead__email', 'lead__first_name',
                     'lead__last_name', 'name', )
    list_filter = ('name', )
    readonly_fields = ('created', )

    def lead_email(self, obj):
        return obj.lead.email

    def lead_name(self, obj):
        return obj.lead.name()


class EC2InstanceAdmin(admin.ModelAdmin):
    model = CustomerIOEvent
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
        'web_up',
        'ssh_up',
    )
    list_filter = ('status', 'ssh_up', 'tunnel_up', 'web_up', )
    readonly_fields = ('created', 'updated', )
    search_fields = ('instance_id', 'email', 'rpid', 'lead__leadid', )
    list_select_related = ('lead', 'lead__raspberry_pi', )
    actions = (
        'troubleshoot',
        'troubleshoot_fix',
        'update_password',
        'update_ec2_tags',
        'get_currect_state',
        'check_missing',
        'restart',
        'start',
        'stop',
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
        return '<a target="_blank" href="{url}?q={q}">{rpid} v. {version}</a>'.format(
            url=reverse('admin:adsrental_raspberrypi_changelist'),
            rpid=obj.lead.raspberry_pi.rpid,
            version=obj.lead.raspberry_pi.version,
            q=obj.lead.raspberry_pi.rpid,
        )

    def links(self, obj):
        links = []
        if obj.lead and obj.lead.raspberry_pi:
            links.append('<a target="_blank" href="{url}">RDP</a>'.format(
                url=reverse('rdp', kwargs=dict(rpid=obj.rpid)),
            ))
            links.append('<a target="_blank" href="/log/{rpid}">Logs</a>'.format(
                rpid=obj.rpid,
            ))

        links.append('<a href="#" title="ssh -i ~/.ssh/farmbot Administrator@{hostname} -p 40594">Copy SSH</a>'.format(
            hostname=obj.hostname,
        ))
        links.append('<a target="_blank" href="http://{hostname}:13608">CURL</a>'.format(
            hostname=obj.hostname,
        ))
        return ', '.join(links)

    def troubleshoot(self, request, queryset):
        for ec2_instance in queryset:
            ec2_instance.troubleshoot()

    def troubleshoot_fix(self, request, queryset):
        for ec2_instance in queryset:
            ec2_instance.troubleshoot_fix()

    def update_password(self, request, queryset):
        for ec2_instance in queryset:
            ec2_instance.change_password()

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


admin.site.register(User, CustomUserAdmin)
admin.site.register(Lead, LeadAdmin)
admin.site.register(RaspberryPi, RaspberryPiAdmin)
admin.site.register(CustomerIOEvent, CustomerIOEventAdmin)
admin.site.register(EC2Instance, EC2InstanceAdmin)
