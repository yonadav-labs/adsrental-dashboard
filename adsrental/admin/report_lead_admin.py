from __future__ import unicode_literals

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib import messages
from django.utils import timezone
from django.contrib.humanize.templatetags.humanize import naturaltime

from adsrental.forms import AdminLeadBanForm
from adsrental.models.lead import ReportProxyLead
from adsrental.models.ec2_instance import EC2Instance
from adsrental.admin.list_filters import StatusListFilter, RaspberryPiOnlineListFilter, TouchCountListFilter, AccountTypeListFilter, WrongPasswordListFilter, RaspberryPiFirstTestedListFilter, BundlerListFilter


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
        'utm_source',
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
        'bundler_field',
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
        RaspberryPiOnlineListFilter,
        AccountTypeListFilter,
        WrongPasswordListFilter,
        TouchCountListFilter,
        RaspberryPiFirstTestedListFilter,
        'company',
        BundlerListFilter,
        'is_sync_adsdb',
        'bundler_paid',
        'pi_delivered',
    )
    readonly_fields = ('created', 'updated', )
    search_fields = ('leadid', 'account_name', 'first_name', 'last_name', 'raspberry_pi__rpid', 'email', )
    list_select_related = ('raspberry_pi', 'bundler', )
    actions = (
        'mark_as_qualified',
        'mark_as_disqualified',
        'ban',
        'unban',
        'report_wrong_password',
        'report_correct_password',
        'prepare_for_reshipment',
        'touch',
        'restart_raspberry_pi',
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

    def bundler_field(self, obj):
        if obj.bundler:
            return obj.bundler

        return obj.utm_source

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

    def mark_as_qualified(self, request, queryset):
        for lead in queryset:
            if lead.is_banned():
                messages.warning(request, 'Lead {} is {}, skipping'.format(lead.email, lead.status))
                continue

            lead.qualify(request.user)
            if lead.assign_raspberry_pi():
                messages.success(
                    request, 'Lead {} has new Raspberry Pi assigned: {}'.format(lead.email, lead.raspberry_pi.rpid))

            EC2Instance.launch_for_lead(lead)
            if lead.add_shipstation_order():
                messages.success(
                    request, '{} order created: {}'.format(lead.email, lead.shipstation_order_number))
            else:
                messages.info(
                    request, 'Lead {} order already exists: {}. If you want to ship another, clear shipstation_order_number field first'.format(lead.email, lead.shipstation_order_number))

    def mark_as_disqualified(self, request, queryset):
        for lead in queryset:
            if lead.is_banned():
                messages.warning(request, 'Lead {} is {}, skipping'.format(lead.email, lead.status))
                continue

            lead.disqualify(request.user)
            messages.info(request, 'Lead {} is disqualified.'.format(lead.email))

    def restart_raspberry_pi(self, request, queryset):
        for lead in queryset:
            if not lead.raspberry_pi:
                messages.warning(request, 'Lead {} does not haave RaspberryPi assigned, skipping'.format(lead.email))
                continue

            lead.raspberry_pi.restart_required = True
            lead.raspberry_pi.save()
            messages.info(request, 'Lead {} RPi restart successfully requested. RPi and tunnel should be online in two minutes.'.format(lead.email))

    def ban(self, request, queryset):
        if 'do_action' in request.POST:
            form = AdminLeadBanForm(request.POST)
            if form.is_valid():
                reason = form.cleaned_data['reason']
                for lead in queryset:
                    lead.ban(request.user, reason)
                    if lead.get_ec2_instance():
                        lead.get_ec2_instance().stop()
                    messages.info(request, 'Lead {} is banned.'.format(lead.email))
                return
        else:
            form = AdminLeadBanForm()

        return render(request, 'admin/action_with_form.html', {
            'action_name': 'ban',
            'title': 'Choose reason to ban following leads',
            'button': 'Ban',
            'objects': queryset,
            'form': form,
        })

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
            if lead.raspberry_pi:
                lead.prepare_for_reshipment(request.user)
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

    mark_as_qualified.short_description = 'Mark as Qualified, Assign RPi, create Shipstation order'

    bundler_field.short_description = 'Bundler'
    bundler_field.admin_order_field = 'utm_source'
