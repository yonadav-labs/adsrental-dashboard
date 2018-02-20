
from __future__ import unicode_literals

from django.contrib import admin
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import naturaltime

from adsrental.models.lead import Lead
from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.models.ec2_instance import EC2Instance
from adsrental.admin.list_filters import StatusListFilter, RaspberryPiOnlineListFilter, AccountTypeListFilter, WrongPasswordListFilter, RaspberryPiFirstTestedListFilter, TouchCountListFilter
from adsrental.utils import ShipStationClient


class LeadAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }

    model = Lead
    list_display = (
        'id_field',
        'name',
        'status_field',
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
        'online',
        'wrong_password_date_field',
        'pi_delivered',
        'bundler_paid',
    )
    list_filter = (
        StatusListFilter,
        RaspberryPiOnlineListFilter,
        AccountTypeListFilter,
        WrongPasswordListFilter,
        TouchCountListFilter,
        RaspberryPiFirstTestedListFilter,
        'company',
        'utm_source',
        'is_sync_adsdb',
        'bundler_paid',
        'pi_delivered',
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
        'update_from_shipstation',
        'update_pi_delivered',
        'mark_as_qualified',
        'mark_as_disqualified',
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
        return obj.leadid

    def name(self, obj):
        return u'{} {}'.format(
            obj.first_name,
            obj.last_name,
        )

    def status_field(self, obj):
        return '<a target="_blank" href="{url}?q={q}" title="Show changes">{status}</a>'.format(
            url=reverse('admin:adsrental_leadchange_changelist'),
            q=obj.leadid,
            status=obj.status,
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

    def tested_field(self, obj):
        if obj.raspberry_pi and obj.raspberry_pi.first_tested:
            return '<img src="/static/admin/img/icon-yes.svg" title="{}" alt="True">'.format(
                naturaltime(obj.raspberry_pi.first_tested),
            )

        return None

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

        return '<span title="{}">{}</span> <a href="{}" target="_blank">Fix</a>'.format(
            obj.wrong_password_date,
            naturaltime(obj.wrong_password_date),
            reverse('dashboard_set_password', kwargs=dict(lead_id=obj.leadid)),
        )

    def raspberry_pi_link(self, obj):
        result = []
        if obj.raspberry_pi:
            result.append('<a target="_blank" href="{url}?q={rpid}">{rpid}</a> (<a target="_blank" href="{log_url}">Logs</a>, <a href="{rdp_url}">RDP</a>, <a href="{config_url}">Config file</a>)'.format(
                log_url=reverse('show_log_dir', kwargs={'rpid': obj.raspberry_pi.rpid}),
                rdp_url=reverse('rdp', kwargs={'rpid': obj.raspberry_pi.rpid}),
                url=reverse('admin:adsrental_raspberrypi_changelist'),
                config_url=reverse('farming_pi_config', kwargs={'rpid': obj.raspberry_pi.rpid}),
                rpid=obj.raspberry_pi,
            ))

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

        return '\n'.join(result)

    def update_from_shipstation(self, request, queryset):
        for lead in queryset:
            lead.update_from_shipstation()

    def update_pi_delivered(self, request, queryset):
        for lead in queryset:
            lead.update_pi_delivered()

    def mark_as_qualified(self, request, queryset):
        for lead in queryset:
            if lead.is_banned():
                messages.warning(request, 'Lead {} is {}, skipping'.format(lead.email, lead.status))
                continue

            lead.set_status(Lead.STATUS_QUALIFIED, request.user)
            if not lead.raspberry_pi:
                lead.raspberry_pi = RaspberryPi.get_free_or_create()
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
                    request, 'Lead {} order already exists: {}. If you want to ship another, clear shipstation_order_number field first'.format(lead.email, lead.shipstation_order_number))
                continue

            order = shipstation_client.add_lead_order(lead)
            messages.success(
                request, '{} order created: {}'.format(lead.str(), order.order_key))

    def mark_as_disqualified(self, request, queryset):
        for lead in queryset:
            lead.set_status(Lead.STATUS_DISQUALIFIED)
            messages.success(request, 'Lead {} is disqualified'.format(lead.email))

    def start_ec2(self, request, queryset):
        for lead in queryset:
            EC2Instance.launch_for_lead(lead)

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
            if lead.ban(request.user):
                if lead.get_ec2_instance():
                    lead.get_ec2_instance().stop()
                messages.info(request, 'Lead {} is banned.'.format(lead.email))

    def unban(self, request, queryset):
        for lead in queryset:
            if lead.unban(request.user):
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

    status_field.allow_tags = True
    status_field.short_description = 'Status'
    status_field.admin_order_field = 'status'

    wrong_password_date_field.short_description = 'Wrong Password'
    wrong_password_date_field.allow_tags = True
    wrong_password_date_field.admin_order_field = 'wrong_password_date'

    tested_field.allow_tags = True
    tested_field.short_description = 'Tested'

    last_touch.allow_tags = True
    last_touch.admin_order_field = 'last_touch_date'
    id_field.short_description = 'ID'
    mark_as_qualified.short_description = 'Mark as Qualified, Assign RPi, create Shipstation order'
    ec2_instance_link.short_description = 'EC2 instance'
    ec2_instance_link.allow_tags = True
    start_ec2.short_description = 'Start EC2 instance'
    restart_ec2.short_description = 'Restart EC2 instance'
    email_field.allow_tags = True
    email_field.short_description = 'Email'
    email_field.admin_order_field = 'email'
    online.boolean = True
    online.admin_order_field = 'raspberry_pi__first_seen'
    raspberry_pi_link.short_description = 'Raspberry PI'
    raspberry_pi_link.allow_tags = True
    first_seen.empty_value_display = 'Never'
    first_seen.admin_order_field = 'raspberry_pi__first_seen'
    first_seen.allow_tags = True
    last_seen.empty_value_display = 'Never'
    last_seen.admin_order_field = 'raspberry_pi__last_seen'
    last_seen.allow_tags = True
    facebook_account_column.short_description = 'Facebook Account'
    facebook_account_column.allow_tags = True
    google_account_column.admin_order_field = 'facebook_account'
    google_account_column.short_description = 'Google Account'
    google_account_column.allow_tags = True
    google_account_column.admin_order_field = 'google_account'
