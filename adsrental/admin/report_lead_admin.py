from __future__ import unicode_literals

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils import timezone
from django.contrib.humanize.templatetags.humanize import naturaltime

from adsrental.models.lead import ReportProxyLead
from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.models.ec2_instance import EC2Instance
from adsrental.admin.list_filters import StatusListFilter, RaspberryPiOnlineListFilter, TouchCountListFilter, AccountTypeListFilter
from adsrental.utils import ShipStationClient


class ReportLeadAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }

    model = ReportProxyLead
    admin_caching_enabled = True
    list_display = (
        'leadid',
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
        RaspberryPiOnlineListFilter,
        TouchCountListFilter,
        'is_sync_adsdb',
        'bundler_paid',
        'pi_delivered',
    )
    readonly_fields = ('created', 'updated', )
    search_fields = ('leadid', 'account_name', 'first_name', 'last_name', 'raspberry_pi__rpid', 'email', )
    list_select_related = ('raspberry_pi', )
    actions = (
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

    def create_shipstation_order(self, request, queryset):
        for lead in queryset:
            if lead.is_banned():
                messages.warning(request, 'Lead {} is {}, skipping'.format(lead.email, lead.status))
                continue

            lead.set_status(ReportProxyLead.STATUS_QUALIFIED, request.user)
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

    last_touch.allow_tags = True
    raspberry_pi_link.allow_tags = True

    last_touch.admin_order_field = 'last_touch_date'
    raspberry_pi_link.admin_order_field = 'raspberry_pi__rpid'
    first_seen.admin_order_field = 'raspberry_pi__first_seen'
    last_seen.admin_order_field = 'raspberry_pi__last_seen'
    account_type.admin_order_field = 'facebook_account'

    raspberry_pi_link.short_description = 'RPID'
