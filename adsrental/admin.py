from __future__ import unicode_literals

import unicodecsv as csv
import datetime
from dateutil.relativedelta import relativedelta

from django.http import HttpResponse
from django.contrib import admin
from django.conf import settings
from django.contrib.auth.admin import UserAdmin
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils import timezone
from django.contrib.admin import SimpleListFilter
from django.core.urlresolvers import reverse
from django.contrib import messages

from adsrental.models.lead import Lead, ReportProxyLead
from adsrental.models import User, RaspberryPi, CustomerIOEvent, EC2Instance, Bundler, LeadHistory, LeadHistoryMonth, LeadChange
from salesforce_handler.models import Lead as SFLead
from adsrental.utils import ShipStationClient


class StatusListFilter(SimpleListFilter):
    title = 'Status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return Lead.STATUS_CHOICES + [
            ('Active',  'Active'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'Active':
            return queryset.filter(status__in=Lead.STATUSES_ACTIVE)
        if self.value():
            return queryset.filter(status=self.value())


class TouchCountListFilter(SimpleListFilter):
    title = 'Touch Count'
    parameter_name = 'touch_count'

    def lookups(self, request, model_admin):
        return (
            ('10', 'More than 10 only'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(touch_count__gte=int(self.value()))


class OnlineListFilter(SimpleListFilter):
    title = 'RaspberryPi online state'
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
            return queryset.filter(raspberry_pi__last_seen__gt=timezone.now() - datetime.timedelta(hours=RaspberryPi.online_hours_ttl))
        if self.value() == 'offline':
            return queryset.filter(raspberry_pi__last_seen__lte=timezone.now() - datetime.timedelta(hours=RaspberryPi.online_hours_ttl))
        if self.value() == 'offline_2days':
            return queryset.filter(raspberry_pi__last_seen__lte=timezone.now() - datetime.timedelta(hours=RaspberryPi.online_hours_ttl + 2 * 24))
        if self.value() == 'offline_5days':
            return queryset.filter(raspberry_pi__last_seen__lte=timezone.now() - datetime.timedelta(hours=RaspberryPi.online_hours_ttl + 5 * 24))


class RaspberryPiOnlineListFilter(SimpleListFilter):
    title = 'RaspberryPi online state'
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
            return queryset.filter(last_seen__gt=timezone.now() - datetime.timedelta(hours=RaspberryPi.online_hours_ttl))
        if self.value() == 'offline':
            return queryset.filter(last_seen__lte=timezone.now() - datetime.timedelta(hours=RaspberryPi.online_hours_ttl))
        if self.value() == 'offline_2days':
            return queryset.filter(last_seen__lte=timezone.now() - datetime.timedelta(hours=RaspberryPi.online_hours_ttl + 2 * 24))
        if self.value() == 'offline_5days':
            return queryset.filter(last_seen__lte=timezone.now() - datetime.timedelta(hours=RaspberryPi.online_hours_ttl + 5 * 24))


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
            return queryset.filter(raspberry_pi__tunnel_last_tested__gt=timezone.now() - datetime.timedelta(hours=RaspberryPi.tunnel_online_hours_ttl))
        if self.value() == 'offline':
            return queryset.filter(raspberry_pi__tunnel_last_tested__lte=timezone.now() - datetime.timedelta(hours=RaspberryPi.tunnel_online_hours_ttl))
        if self.value() == 'offline_2days':
            return queryset.filter(raspberry_pi__tunnel_last_tested__lte=timezone.now() - datetime.timedelta(hours=RaspberryPi.tunnel_online_hours_ttl + 2 * 24))
        if self.value() == 'offline_5days':
            return queryset.filter(raspberry_pi__tunnel_last_tested__lte=timezone.now() - datetime.timedelta(hours=RaspberryPi.tunnel_online_hours_ttl + 5 * 24))


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
            return queryset.filter(tunnel_last_tested__gt=timezone.now() - datetime.timedelta(hours=RaspberryPi.tunnel_online_hours_ttl))
        if self.value() == 'offline':
            return queryset.filter(tunnel_last_tested__lte=timezone.now() - datetime.timedelta(hours=RaspberryPi.tunnel_online_hours_ttl))
        if self.value() == 'offline_2days':
            return queryset.filter(tunnel_last_tested__lte=timezone.now() - datetime.timedelta(hours=RaspberryPi.tunnel_online_hours_ttl + 2 * 24))
        if self.value() == 'offline_5days':
            return queryset.filter(tunnel_last_tested__lte=timezone.now() - datetime.timedelta(hours=RaspberryPi.tunnel_online_hours_ttl + 5 * 24))


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
            return queryset.filter(wrong_password_date__isnull=True)
        if self.value() == 'yes':
            return queryset.filter(wrong_password_date__isnull=False)
        if self.value() == 'yes_2days':
            return queryset.filter(wrong_password_date__lte=timezone.now() - datetime.timedelta(hours=2 * 24))
        if self.value() == 'yes_5days':
            return queryset.filter(wrong_password_date__lte=timezone.now() - datetime.timedelta(hours=5 * 24))


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
    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }

    model = Lead
    list_display = (
        'id_field',
        # 'usps_tracking_code',
        'account_name',
        'name',
        'status',
        'email_field',
        'phone',
        'utm_source',
        'google_account_column',
        'facebook_account_column',
        'raspberry_pi_link',
        'ec2_instance_link',
        'tested_field',
        'last_touch',
        'first_seen',
        'last_seen',
        'tunnel_last_tested',
        'online',
        'tunnel_online',
        'wrong_password_date_field',
        'pi_delivered',
        'bundler_paid',
    )
    list_filter = (StatusListFilter, OnlineListFilter, TunnelOnlineListFilter, AccountTypeListFilter,
                   WrongPasswordListFilter, 'utm_source', 'bundler_paid', 'pi_delivered', 'tested', )
    list_select_related = ('raspberry_pi', 'ec2instance', )
    search_fields = (
        'leadid',
        'account_name',
        'first_name',
        'last_name',
        'raspberry_pi__rpid',
        'email',
    )
    actions = (
        'update_from_salesforce',
        'update_salesforce',
        'update_from_shipstation',
        'update_pi_delivered',
        'create_shipstation_order',
        'start_ec2',
        'restart_ec2',
        'restart_raspberry_pi',
        'ban',
        'unban',
        'report_wrong_password',
        'report_correct_password',
        'prepare_for_reshipment',
        'touch',
    )
    readonly_fields = ('created', 'updated', )
    raw_id_fields = ('raspberry_pi', )

    def id_field(self, obj):
        if obj.sf_leadid:
            return obj.sf_leadid

        return ('LOCAL: {}'.format(obj.leadid))

    def name(self, obj):
        return u'{} {}'.format(
            obj.first_name,
            obj.last_name,
        )

    def email_field(self, obj):
        return '{email} (<a href="{sf_url}?q={email}" target="_blank">SF Local</a>, <a href="https://na40.salesforce.com/{sf_leadid}" target="_blank">SF</a>)'.format(
            email=obj.email,
            sf_url=reverse('admin:salesforce_handler_lead_changelist'),
            sf_leadid=obj.sf_leadid,
        )

    def last_touch(self, obj):
        return '<span title="Touched {} times">{}</span>'.format(
            obj.touch_count,
            naturaltime(obj.last_touch_date) if obj.last_touch_date else 'Never',
        )

    def online(self, obj):
        return obj.raspberry_pi.online() if obj.raspberry_pi else False

    def tunnel_online(self, obj):
        return obj.raspberry_pi.tunnel_online() if obj.raspberry_pi else False

    def tested_field(self, obj):
        if obj.raspberry_pi and obj.raspberry_pi.first_tested:
            return True

        return False

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
            '<img src="/static/admin/img/icon-yes.svg" alt="True">' if obj.facebook_account else '',
            obj.facebook_account_status,
        )

    def google_account_column(self, obj):
        return '{} {}'.format(
            '<img src="/static/admin/img/icon-yes.svg" alt="True">' if obj.google_account else '',
            obj.google_account_status,
        )

    def wrong_password_date_field(self, obj):
        if not obj.wrong_password_date:
            return None

        return '<span title="{}">{}</span>'.format(obj.wrong_password_date, naturaltime(obj.wrong_password_date))

    def raspberry_pi_link(self, obj):
        result = []
        if obj.raspberry_pi:
            result.append('<a target="_blank" href="{url}?q={rpid}">{rpid}</a> (<a target="_blank" href="/log/{rpid}">Logs</a>, <a href="{rdp_url}">RDP</a>, <a href="{config_url}">Config file</a>)'.format(
                rdp_url=reverse('rdp', kwargs={'rpid': obj.raspberry_pi}),
                url=reverse('admin:adsrental_raspberrypi_changelist'),
                config_url=reverse('farming_pi_config', kwargs={'rpid': obj.raspberry_pi}),
                rpid=obj.raspberry_pi,
            ))

        for error in obj.find_raspberry_pi_errors():
            result.append('<img src="/static/admin/img/icon-no.svg" title="{}" alt="False">'.format(error))

        return '\n'.join(result)

    def ec2_instance_link(self, obj):
        result = []
        ec2_instance = obj.get_ec2_instance()
        if ec2_instance:
            result.append('<a target="_blank" href="{url}?q={q}">{ec2_instance}</a>'.format(
                url=reverse('admin:adsrental_ec2instance_changelist'),
                ec2_instance=ec2_instance,
                q=ec2_instance.instance_id,
            ))

        for error in obj.find_ec2_instance_errors():
            result.append('<img src="/static/admin/img/icon-no.svg" title="{}" alt="False">'.format(error))

        return '\n'.join(result)

    def update_from_salesforce(self, request, queryset):
        sf_lead_emails = []
        leads_map = {}
        for lead in queryset:
            leads_map[lead.email] = lead
            sf_lead_emails.append(lead.email)

        sf_leads = SFLead.objects.filter(
            email__in=sf_lead_emails).simple_select_related('raspberry_pi')
        for sf_lead in sf_leads:
            Lead.upsert_from_sf(sf_lead, leads_map.get(sf_lead.email))

    def update_salesforce(self, request, queryset):
        sf_lead_emails = []
        leads_map = {}
        for lead in queryset:
            leads_map[lead.email] = lead
            sf_lead_emails.append(lead.email)

        sf_leads = SFLead.objects.filter(
            email__in=sf_lead_emails).simple_select_related('raspberry_pi')
        for sf_lead in sf_leads:
            Lead.upsert_to_sf(sf_lead, leads_map.get(sf_lead.email))

    def update_from_shipstation(self, request, queryset):
        for lead in queryset:
            lead.update_from_shipstation()

    def update_pi_delivered(self, request, queryset):
        for lead in queryset:
            lead.update_pi_delivered()

    def create_shipstation_order(self, request, queryset):
        for lead in queryset:
            if not lead.raspberry_pi:
                lead.raspberry_pi = RaspberryPi.objects.filter(lead__isnull=True, rpid__startswith='RP', first_seen__isnull=True).order_by('rpid').first()
                lead.save()
                lead.raspberry_pi.leadid = lead.leadid
                lead.raspberry_pi.first_seen = None
                lead.raspberry_pi.last_seen = None
                lead.raspberry_pi.first_tested = None
                lead.raspberry_pi.tunnel_last_tested = None
                lead.raspberry_pi.save()
                messages.success(
                    request, 'Lead {} has new Raspberry Pi assigned: {}'.format(lead.email, lead.raspberry_pi.rpid))

            EC2Instance.launch_for_lead(lead)

            shipstation_client = ShipStationClient()
            if shipstation_client.get_lead_order_data(lead):
                messages.info(
                    request, 'Lead {} order already exists'.format(lead.email))
                continue

            order = shipstation_client.add_lead_order(lead)
            messages.success(
                request, '{} order created: {}'.format(lead.str(), order.order_key))

    def start_ec2(self, request, queryset):
        for lead in queryset:
            EC2Instance.launch_for_lead(self)

    def restart_ec2(self, request, queryset):
        for lead in queryset:
            lead.ec2instance.restart()

    def restart_raspberry_pi(self, request, queryset):
        for lead in queryset:
            lead.raspberry_pi.restart_required = True
            lead.raspberry_pi.save()
        messages.info(request, 'Lead {} RPi restart successfully requested. RPi and tunnel should be online in two minutes.'.format(lead.email))

    def ban(self, request, queryset):
        for lead in queryset:
            if lead.ban():
                if lead.get_ec2_instance():
                    lead.get_ec2_instance().stop()
                messages.info(request, 'Lead {} is banned.'.format(lead.email))

    def unban(self, request, queryset):
        for lead in queryset:
            if lead.unban():
                EC2Instance.launch_for_lead(lead)
                messages.info(request, 'Lead {} is unbanned.'.format(lead.email))

    def report_wrong_password(self, request, queryset):
        for lead in queryset:
            if lead.wrong_password_date is None:
                lead.wrong_password_date = timezone.now()
                lead.save()
                messages.info(request, 'Lead {} password is marked as wrong.'.format(lead.email))

    def report_correct_password(self, request, queryset):
        for lead in queryset:
            if lead.wrong_password_date is not None:
                lead.wrong_password_date = None
                lead.save()
                messages.info(request, 'Lead {} password is marked as correct.'.format(lead.email))

    def touch(self, request, queryset):
        for lead in queryset:
            lead.touch()
            messages.info(request, 'Lead {} has been touched for {} time.'.format(lead.email, lead.touch_count))

    def prepare_for_reshipment(self, request, queryset):
        for lead in queryset:
            raspberry_pi = lead.raspberry_pi
            if raspberry_pi:
                raspberry_pi.first_tested = None
                raspberry_pi.last_seen = None
                raspberry_pi.first_seen = None
                raspberry_pi.tunnel_last_tested = None
                raspberry_pi.save()
                messages.info(request, 'Lead {} is prepared. You can now flash and test it.'.format(lead.email))
            else:
                messages.warning(request, 'Lead {} has no assigned RaspberryPi. Assign a new one first.'.format(lead.email))

    wrong_password_date_field.short_description = 'Wrong Password'
    wrong_password_date_field.allow_tags = True
    wrong_password_date_field.admin_order_field = 'wrong_password_date'

    tested_field.boolean = True
    tested_field.short_description = 'Tested'

    last_touch.allow_tags = True
    last_touch.admin_order_field = 'last_touch_date'
    id_field.short_description = 'ID'
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
    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }

    model = RaspberryPi
    list_display = ('rpid', 'lead_link', 'ec2_instance_link', 'first_tested_field', 'first_seen_field',
                    'last_seen_field', 'tunnel_last_tested_field', 'online', 'tunnel_online', )
    search_fields = ('leadid', 'rpid', )
    list_filter = (RaspberryPiOnlineListFilter,
                   RaspberryPiTunnelOnlineListFilter, )
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

        for error in obj.lead.find_ec2_instance_errors():
            result.append('<img src="/static/admin/img/icon-no.svg" title="{}" alt="False">'.format(error))

        return '\n'.join(result)

    def online(self, obj):
        return obj.online()

    def tunnel_online(self, obj):
        return obj.tunnel_online()

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

    def tunnel_last_tested_field(self, obj):
        if obj.tunnel_last_tested is None:
            return None

        tunnel_last_tested = obj.get_tunnel_last_tested()
        return u'<span title="{}">{}</span>'.format(tunnel_last_tested, naturaltime(tunnel_last_tested))

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
    tunnel_online.boolean = True
    first_tested_field.short_description = 'Tested'
    first_tested_field.allow_tags = True
    first_seen_field.short_description = 'First Seen'
    first_seen_field.empty_value_display = 'Never'
    first_seen_field.allow_tags = True
    last_seen_field.short_description = 'Last Seen'
    last_seen_field.empty_value_display = 'Never'
    last_seen_field.allow_tags = True
    tunnel_last_tested_field.short_description = 'Tunnel Last Tested'
    tunnel_last_tested_field.empty_value_display = 'Never'
    tunnel_last_tested_field.allow_tags = True


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


class LeadRaspberryPiOnlineListFilter(SimpleListFilter):
    title = 'RaspberryPi online state'
    parameter_name = 'online'

    def lookups(self, request, model_admin):
        return (
            ('online_5m', 'Online last 5 min'),
            ('online', 'Online last hour'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'online_5m':
            return queryset.filter(lead__raspberry_pi__last_seen__gt=timezone.now() - datetime.timedelta(minutes=5))
        if self.value() == 'online':
            return queryset.filter(lead__raspberry_pi__last_seen__gt=timezone.now() - datetime.timedelta(hours=RaspberryPi.online_hours_ttl))


class LeadRaspberryPiVersionListFilter(SimpleListFilter):
    title = 'RaspberryPi version'
    parameter_name = 'version'

    def lookups(self, request, model_admin):
        return (
            ('latest', 'Only {}'.format(settings.RASPBERRY_PI_VERSION)),
            ('old', 'Old versions'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'latest':
            return queryset.filter(lead__raspberry_pi__version=settings.RASPBERRY_PI_VERSION)
        if self.value() == 'online':
            return queryset.exclude(lead__raspberry_pi__version=settings.RASPBERRY_PI_VERSION)


class EC2InstanceAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }

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
        # 'ssh_up',
    )
    list_filter = (
        'status',
        'tunnel_up',
        'web_up',
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


class ReportLeadAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }

    list_display = (
        'sf_leadid',
        # 'rpid',
        'first_name',
        'last_name',
        # 'utm_source',
        'status',
        # 'street',
        # 'city',
        # 'state',
        # 'postal_code',
        'pi_delivered',
        'is_sync_adsdb',
        'account_type',
        'company',
        'email',
        # 'phone',
        'raspberry_pi_link',
        'utm_source',
        'bundler_paid',
        'billed',
        'touch_count',
        'last_touch',
        'wrong_password',
        'first_seen',
        'last_seen',
    )
    list_filter = (
        StatusListFilter,
        'company',
        AccountTypeListFilter,
        OnlineListFilter,
        TouchCountListFilter,
        'is_sync_adsdb',
        'bundler_paid',
        'pi_delivered',
    )
    readonly_fields = ('created', 'updated', )
    search_fields = ('leadid', 'account_name', 'first_name', 'last_name', 'raspberry_pi__rpid', 'email', )
    list_select_related = ('raspberry_pi', )
    list_per_page = 500

    def rpid(self, obj):
        return obj.raspberry_pi and obj.raspberry_pi.rpid

    def account_type(self, obj):
        if obj.facebook_account:
            return 'Facebook'
        if obj.google_account:
            return 'Google'
        return 'n/a'

    def first_seen(self, obj):
        return obj.raspberry_pi and obj.raspberry_pi.first_seen

    def last_seen(self, obj):
        return obj.raspberry_pi and obj.raspberry_pi.last_seen

    def last_touch(self, obj):
        return '<span title="Touched {} times">{}</span>'.format(
            obj.touch_count,
            naturaltime(obj.last_touch_date) if obj.last_touch_date else 'Never',
        )

    def raspberry_pi_link(self, obj):
        result = []
        if obj.raspberry_pi:
            result.append('<a target="_blank" href="{url}?q={rpid}">{rpid}</a>'.format(
                url=reverse('admin:adsrental_raspberrypi_changelist'),
                rpid=obj.raspberry_pi,
            ))

        return result

    last_touch.allow_tags = True
    raspberry_pi_link.allow_tags = True

    last_touch.admin_order_field = 'last_touch_date'
    raspberry_pi_link.admin_order_field = 'raspberry_pi__rpid'
    first_seen.admin_order_field = 'raspberry_pi__first_seen'
    last_seen.admin_order_field = 'raspberry_pi__last_seen'
    account_type.admin_order_field = 'facebook_account'

    raspberry_pi_link.short_description = 'RPID'


class BundlerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'utm_source', 'adsdb_id', 'email', 'phone', )


class LeadHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'lead', 'date', 'checks_offline', 'checks_online', 'checks_wrong_password', )


class DateMonthListFilter(SimpleListFilter):
    title = 'Date'
    parameter_name = 'date'

    def lookups(self, request, model_admin):
        month_start = datetime.date.today().replace(day=1)
        choices = []
        for i in range(3):
            d = month_start - relativedelta(months=i)
            choices.append((d.strftime(settings.SYSTEM_DATE_FORMAT), d.strftime('%b %Y')))

        return choices

    def queryset(self, request, queryset):
        if self.value():
            d = datetime.datetime.strptime(self.value(), settings.SYSTEM_DATE_FORMAT).date()
            return queryset.filter(date=d)


class HistoryStatusListFilter(SimpleListFilter):
    title = 'Status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('hide_zeroes', 'Hide zeroes', ),
        )

    def queryset(self, request, queryset):
        if self.value() == 'hide_zeroes':
            return queryset.filter(days_online__gt=0)


class LeadHistoryMonthAdmin(admin.ModelAdmin):
    class Meta:
        model = LeadHistoryMonth

    list_per_page = 5000
    list_display = (
        'id',
        'lead_link',
        'rpid',
        'lead_address',
        'days_online',
        'days_offline',
        'days_wrong_password',
        'amount',
    )
    csv_fields = (
        ('leadid', 'Lead'),
        ('rpid', 'RPID', ),
        ('lead__first_name', 'First Name', ),
        ('lead__last_name', 'Last Name', ),
        ('lead__street', 'Street', ),
        ('lead__city', 'City', ),
        ('lead__state', 'State', ),
        ('lead__postal_code', 'Postal Code', ),
        ('days_online', 'Days online'),
        ('days_offline', 'Days offline'),
        ('days_wrong_password', 'Days wrong password'),
        ('amount', 'Amount'),
    )
    search_fields = ('lead__raspberry_pi__rpid', 'lead__first_name', 'lead__last_name', 'lead__email', 'lead__phone', )
    list_filter = (DateMonthListFilter, HistoryStatusListFilter, )
    list_select_related = ('lead', 'lead__raspberry_pi')
    actions = ('export_as_csv', )

    def leadid(self, obj):
        return obj.lead and obj.lead.sf_leadid

    def rpid(self, obj):
        return obj.lead and obj.lead.raspberry_pi and obj.lead.raspberry_pi.rpid

    def lead_address(self, obj):
        return obj.lead and obj.lead.get_address()

    def get_queryset(self, request):
        queryset = super(LeadHistoryMonthAdmin, self).get_queryset(request)
        if 'date' not in request.GET:
            queryset = queryset.filter(date=datetime.date.today().replace(day=1))

        return queryset

    def amount(self, obj):
        return '${}'.format(round(obj.get_amount(), 2))

    def lead_link(self, obj):
        lead = obj.lead
        return '<a target="_blank" href="{url}?q={q}">{lead}</a>'.format(
            url=reverse('admin:adsrental_lead_changelist'),
            lead=lead.name(),
            q=lead.leadid,
        )

    def export_as_csv(self, request, queryset):
        field_names = [i[0] for i in self.csv_fields]
        field_titles = [i[1] for i in self.csv_fields]
        date = (datetime.datetime.strptime(request.GET.get('date'), settings.SYSTEM_DATE_FORMAT) if request.GET.get('date') else timezone.now()).date()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=check_report_{month}_{year}.csv'.format(
            month=date.strftime('%b').lower(),
            year=date.strftime('%Y'),
        )

        writer = csv.writer(response, encoding='utf-8')
        writer.writerow(field_titles)
        for obj in queryset:
            row = []
            for field in field_names:
                if hasattr(self, field) and callable(getattr(self, field)):
                    row.append(getattr(self, field)(obj))
                    continue
                if hasattr(obj, field) and callable(getattr(obj, field)):
                    row.append(getattr(obj, field)())
                    continue

                item = obj
                for subfield in field.split('__'):
                    item = getattr(item, subfield)
                row.append(item)
            writer.writerow(row)
        return response

    lead_link.short_description = 'Lead'
    lead_link.allow_tags = True


class LeadChangeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'lead_link',
        'field',
        'value',
        'old_value',
        'created',
    )

    def lead_link(self, obj):
        lead = obj.lead
        return '<a target="_blank" href="{url}?q={q}">{lead}</a>'.format(
            url=reverse('admin:adsrental_lead_changelist'),
            lead=lead.name(),
            q=lead.leadid,
        )

    lead_link.short_description = 'Lead'
    lead_link.allow_tags = True


admin.site.register(User, CustomUserAdmin)
admin.site.register(Lead, LeadAdmin)
admin.site.register(RaspberryPi, RaspberryPiAdmin)
admin.site.register(CustomerIOEvent, CustomerIOEventAdmin)
admin.site.register(EC2Instance, EC2InstanceAdmin)
admin.site.register(ReportProxyLead, ReportLeadAdmin)
admin.site.register(Bundler, BundlerAdmin)
admin.site.register(LeadHistory, LeadHistoryAdmin)
admin.site.register(LeadHistoryMonth, LeadHistoryMonthAdmin)
admin.site.register(LeadChange, LeadChangeAdmin)
