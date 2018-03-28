from __future__ import unicode_literals

from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.shortcuts import render
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import naturaltime

from adsrental.models.lead_account import LeadAccount
from adsrental.models.ec2_instance import EC2Instance
from adsrental.forms import AdminLeadAccountBanForm, AdminLeadAccountPasswordForm
from adsrental.admin.list_filters import WrongPasswordListFilter, QualifiedDateListFilter, StatusListFilter


class LeadAccountAdmin(admin.ModelAdmin):
    model = LeadAccount
    list_display = (
        'id',
        'rpid',
        'lead_link',
        'account_type',
        'status_field',
        'username',
        'password',
        'friends',
        'bundler_paid',
        'adsdb_account_id',
        'wrong_password_date_field',
        'created',
    )
    list_select_related = ('lead', 'lead__ec2instance')
    list_filter = (
        'account_type',
        'bundler_paid',
        StatusListFilter,
        WrongPasswordListFilter,
        QualifiedDateListFilter,
    )
    search_fields = ('lead__leadid', 'username', )
    actions = (
        'mark_as_qualified',
        'mark_as_disqualified',
        'ban',
        'unban',
        'report_wrong_password',
        'report_correct_password',
        'sync_to_adsdb',
    )

    def rpid(self, obj):
        ec2_instance = obj.lead.get_ec2_instance()
        return ec2_instance.rpid if ec2_instance else None

    def lead_link(self, obj):
        lead = obj.lead
        return mark_safe('<a target="_blank" href="{url}?q={q}">{lead}</a>'.format(
            url=reverse('admin:adsrental_lead_changelist'),
            lead=lead.name(),
            q=lead.leadid,
        ))

    def status_field(self, obj):
        title = 'Show changes'
        if obj.ban_reason:
            title = 'Banned for {}'.format(obj.ban_reason)
        return mark_safe('<a target="_blank" href="{url}?q={q}" title="{title}">{status}</a>'.format(
            url=reverse('admin:adsrental_leadchange_changelist'),
            q=obj.leadid,
            title=title,
            status=obj.status,
        ))

    def wrong_password_date_field(self, obj):
        if not obj.wrong_password_date:
            return None

        return mark_safe('<span title="{}">{}</span>'.format(
            obj.wrong_password_date,
            naturaltime(obj.wrong_password_date),
        ))

    def mark_as_qualified(self, request, queryset):
        for lead_account in queryset:
            if lead_account.is_banned():
                messages.warning(request, 'Lead Account {} is {}, skipping'.format(lead_account, lead_account.status))
                continue

            lead_account.qualify(request.user)
            if lead_account.lead.assign_raspberry_pi():
                messages.success(
                    request, 'Lead Account {} has new Raspberry Pi assigned: {}'.format(lead_account, lead_account.lead.raspberry_pi.rpid))

            EC2Instance.launch_for_lead(lead_account.lead)
            if lead_account.lead.add_shipstation_order():
                messages.success(
                    request, '{} order created: {}'.format(lead_account, lead_account.lead.shipstation_order_number))
            else:
                messages.info(
                    request, 'Lead {} order already exists: {}. If you want to ship another, clear shipstation_order_number field first'.format(lead_account, lead_account.lead.shipstation_order_number))

    def mark_as_disqualified(self, request, queryset):
        for lead_account in queryset:
            if lead_account.is_banned():
                messages.warning(request, 'Lead Account {} is {}, skipping'.format(lead_account, lead_account.status))
                continue

            lead_account.disqualify(request.user)
            messages.info(request, 'Lead Account {} is disqualified.'.format(lead_account))


    def ban(self, request, queryset):
        if 'do_action' in request.POST:
            form = AdminLeadAccountBanForm(request.POST)
            if form.is_valid():
                reason = form.cleaned_data['reason']
                for lead_account in queryset:
                    lead_account.ban(request.user, reason)
                    messages.info(request, 'Lead Account {} is banned.'.format(lead_account))
                return None
        else:
            form = AdminLeadAccountBanForm()

        return render(request, 'admin/action_with_form.html', {
            'action_name': 'ban',
            'title': 'Choose reason to ban following leads',
            'button': 'Ban',
            'objects': queryset,
            'form': form,
        })

    def unban(self, request, queryset):
        for lead_account in queryset:
            if lead_account.unban(request.user):
                EC2Instance.launch_for_lead(lead_account.lead)
                messages.info(request, 'Lead Account {} is unbanned.'.format(lead_account))

    def report_wrong_password(self, request, queryset):
        for lead_account in queryset:
            if lead_account.wrong_password_date is None:
                lead_account.wrong_password_date = timezone.now()
                lead_account.save()
                messages.info(request, 'Lead Account {} password is marked as wrong.'.format(lead_account))

    def report_correct_password(self, request, queryset):
        if queryset.count() != 1:
            messages.error(request, 'Only one lead account can be selected.')
            return None

        lead_account = queryset.first()

        if 'do_action' in request.POST:
            form = AdminLeadAccountPasswordForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password']
                lead_account.password = new_password
                lead_account.wrong_password_date = None
                lead_account.save()
                messages.info(request, 'Lead Account {} password is marked as correct.'.format(lead_account))
                return None
        else:
            form = AdminLeadAccountPasswordForm()


        return render(request, 'admin/action_with_form.html', {
            'action_name': 'report_correct_password',
            'title': 'Set new pasword for {}'.format(lead_account),
            'button': 'Save password',
            'objects': queryset,
            'form': form,
        })

    def sync_to_adsdb(self, request, queryset):
        for lead_account in queryset:
            result = lead_account.sync_to_adsdb()
            if result:
                messages.info(request, 'Lead Account {} is synced: {}'.format(lead_account, result))
            else:
                messages.warning(request, 'Lead Account {} does not meet conditions to sync.'.format(lead_account))

    lead_link.short_description = 'Lead'
    lead_link.admin_order_field = 'lead__leadid'

    status_field.short_description = 'Status'
    status_field.admin_order_field = 'status'

    wrong_password_date_field.short_description = 'Wrong Password'
    wrong_password_date_field.admin_order_field = 'wrong_password_date'

    sync_to_adsdb.short_description = 'DEBUG: Sync to ADSDB'

    mark_as_qualified.short_description = 'Mark as Qualified, Assign RPi, create Shipstation order'
