
from __future__ import unicode_literals

from django.contrib import admin
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import naturaltime

from adsrental.models.lead import Lead
from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.models.ec2_instance import EC2Instance
from adsrental.admin.list_filters import StatusListFilter, RaspberryPiOnlineListFilter, RaspberryPiTunnelOnlineListFilter, AccountTypeListFilter, WrongPasswordListFilter
from adsrental.utils import ShipStationClient


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
    list_filter = (
        StatusListFilter,
        RaspberryPiOnlineListFilter,
        RaspberryPiTunnelOnlineListFilter,
        AccountTypeListFilter,
        WrongPasswordListFilter,
        'utm_source',
        'bundler_paid',
        'pi_delivered',
        'tested',
    )
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
        return obj.email

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

    def update_salesforce(self, request, queryset):
        sf_lead_emails = []
        leads_map = {}
        for lead in queryset:
            leads_map[lead.email] = lead
            sf_lead_emails.append(lead.email)

    def update_from_shipstation(self, request, queryset):
        for lead in queryset:
            lead.update_from_shipstation()

    def update_pi_delivered(self, request, queryset):
        for lead in queryset:
            lead.update_pi_delivered()

    def create_shipstation_order(self, request, queryset):
        for lead in queryset:
            if lead.status == Lead.STATUS_AVAILABLE:
                lead.status = Lead.STATUS_QUALIFIED
                lead.save()
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
                    request, 'Lead {} order already exists: {}. If you want to ship another, clear field first'.format(lead.email, lead.shipstation_order_number))
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
    create_shipstation_order.short_description = 'Mark as Qualified, Assign RPi, create Shipstation order'
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
