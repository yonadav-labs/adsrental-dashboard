import datetime

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils import timezone
from django.contrib.admin import SimpleListFilter
from django.core.urlresolvers import reverse

from adsrental.models import User, Lead, RaspberryPi
from salesforce_handler.models import Lead as SFLead


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
        'name', 'status',
        'email',
        'phone',
        'google_account_column',
        'facebook_account_column',
        'raspberry_pi_link',
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
    list_filter = ('status', OnlineListFilter, TunnelOnlineListFilter, AccountTypeListFilter, WrongPasswordListFilter, 'utm_source', 'bundler_paid', 'pi_delivered', 'tested', )
    select_related = ('raspberry_pi', )
    search_fields = ('leadid', 'account_name', 'first_name', 'last_name', 'raspberry_pi__rpid', 'email', )
    actions = ('update_from_salesforce', 'update_salesforce', 'update_from_shipstation', 'update_pi_delivered')

    def name(self, obj):
        return '{} {}'.format(obj.first_name, obj.last_name)

    def online(self, obj):
        return obj.raspberry_pi.online() if obj.raspberry_pi else False

    def tunnel_online(self, obj):
        return obj.raspberry_pi.tunnel_online() if obj.raspberry_pi else False

    def first_seen(self, obj):
        if obj.raspberry_pi is None or obj.raspberry_pi.first_seen is None:
            return None

        return naturaltime(obj.raspberry_pi.get_first_seen())

    def last_seen(self, obj):
        if obj.raspberry_pi is None or obj.raspberry_pi.last_seen is None:
            return None

        return naturaltime(obj.raspberry_pi.get_last_seen())

    def tunnel_last_tested(self, obj):
        if obj.raspberry_pi is None or obj.raspberry_pi.tunnel_last_tested is None:
            return None

        return naturaltime(obj.raspberry_pi.get_tunnel_last_tested())

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
        return '<a target="_blank" href="{url}?q={rpid}">{rpid}</a> (<a target="_blank" href="/log/{rpid}">Logs</a>, <a href="{rdp_url}">RDP</a>)'.format(
            rdp_url=reverse('rdp', kwargs={'rpid': obj.raspberry_pi}),
            url=reverse('admin:adsrental_raspberrypi_changelist'),
            rpid=obj.raspberry_pi,
        )

    def update_from_salesforce(self, request, queryset):
        sf_lead_ids = []
        leads_map = {}
        for lead in queryset:
            leads_map[lead.leadid] = lead
            sf_lead_ids.append(lead.leadid)

        sf_leads = SFLead.objects.filter(id__in=sf_lead_ids).simple_select_related('raspberry_pi')
        for sf_lead in sf_leads:
            Lead.upsert_from_sf(sf_lead, leads_map.get(sf_lead.id))

    def update_salesforce(self, request, queryset):
        sf_lead_ids = []
        leads_map = {}
        for lead in queryset:
            leads_map[lead.leadid] = lead
            sf_lead_ids.append(lead.leadid)

        sf_leads = SFLead.objects.filter(id__in=sf_lead_ids).simple_select_related('raspberry_pi')
        for sf_lead in sf_leads:
            Lead.upsert_to_sf(sf_lead, leads_map.get(sf_lead.id))

    def update_from_shipstation(self, request, queryset):
        for lead in queryset:
            lead.update_from_shipstation()

    def update_pi_delivered(self, request, queryset):
        for lead in queryset:
            lead.update_pi_delivered()

    online.boolean = True
    online.admin_order_field = 'raspberry_pi__first_seen'
    tunnel_online.boolean = True
    tunnel_online.admin_order_field = 'raspberry_pi__tunnel_last_tested'
    raspberry_pi_link.short_description = 'Raspberry PI'
    raspberry_pi_link.allow_tags = True
    first_seen.empty_value_display = 'Never'
    first_seen.admin_order_field = 'raspberry_pi__first_seen'
    last_seen.empty_value_display = 'Never'
    last_seen.admin_order_field = 'raspberry_pi__last_seen'
    tunnel_last_tested.empty_value_display = 'Never'
    tunnel_last_tested.admin_order_field = 'raspberry_pi__tunnel_last_tested'
    facebook_account_column.short_description = 'Facebook Account'
    facebook_account_column.allow_tags = True
    google_account_column.admin_order_field = 'facebook_account'
    google_account_column.short_description = 'Google Account'
    google_account_column.allow_tags = True
    google_account_column.admin_order_field = 'google_account'


class RaspberryPiAdmin(admin.ModelAdmin):
    model = RaspberryPi
    list_display = ('rpid', 'leadid', 'ipaddress', 'ec2_hostname', 'first_seen', 'last_seen', 'tunnel_last_tested', 'online', 'tunnel_online', )
    search_fields = ('leadid', 'rpid', 'ec2_hostname', 'ipaddress', )
    list_filter = (RaspberryPiOnlineListFilter, RaspberryPiTunnelOnlineListFilter, )
    actions = ('update_from_salesforce', )

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

        sf_raspberry_pis = SFLead.objects.filter(name__in=sf_raspberry_pi_names)
        for sf_raspberry_pi in sf_raspberry_pis:
            RaspberryPi.upsert_from_sf(sf_raspberry_pi, raspberry_pis_map.get(sf_raspberry_pi.name))

    online.boolean = True
    tunnel_online.boolean = True
    first_seen.empty_value_display = 'Never'
    last_seen.empty_value_display = 'Never'
    tunnel_last_tested.empty_value_display = 'Never'


admin.site.register(User, CustomUserAdmin)
admin.site.register(Lead, LeadAdmin)
admin.site.register(RaspberryPi, RaspberryPiAdmin)
