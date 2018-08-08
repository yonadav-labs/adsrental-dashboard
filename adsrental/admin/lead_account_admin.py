from __future__ import unicode_literals

from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.shortcuts import render
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import naturaltime

from adsrental.models.lead_account import LeadAccount, ReadOnlyLeadAccount
from adsrental.forms import AdminLeadAccountBanForm, AdminLeadAccountPasswordForm
from adsrental.admin.list_filters import WrongPasswordListFilter, QualifiedDateListFilter, StatusListFilter, BannedDateListFilter, LeadRaspberryPiOnlineListFilter, LeadBundlerListFilter, SecurityCheckpointListFilter, AutoBanListFilter


class LeadAccountAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }

    model = LeadAccount
    list_display = (
        'id',
        'name',
        'lead_link',
        'raspberry_pi_field',
        'account_type',
        'status_field',
        'username',
        'password',
        'friends',
        'bundler_paid',
        'last_touch',
        'first_seen',
        'last_seen',
        'online',
        'touch_count_field',
        'adsdb_account_id',
        'wrong_password_date_field',
        'security_checkpoint_date_field',
        'primary',
        'billed',
        'created',
    )
    list_select_related = ('lead', 'lead__ec2instance')
    list_filter = (
        'account_type',
        LeadRaspberryPiOnlineListFilter,
        'bundler_paid',
        StatusListFilter,
        WrongPasswordListFilter,
        SecurityCheckpointListFilter,
        QualifiedDateListFilter,
        BannedDateListFilter,
        AutoBanListFilter,
        'charge_back',
        'primary',
        'ban_reason',
        LeadBundlerListFilter,
    )
    search_fields = ('lead__leadid', 'lead__email', 'username', )
    actions = (
        'mark_as_qualified',
        'mark_as_disqualified',
        'ban',
        'unban',
        'report_wrong_password',
        'report_correct_password',
        'report_security_checkpoint',
        'report_security_checkpoint_resolved',
        'sync_to_adsdb',
    )
    readonly_fields = (
        'created',
        'updated',
        'status',
        'old_status',
        'wrong_password_date',
        'qualified_date',
        'bundler_paid',
        'bundler_paid_date',
        'primary',
        'active',
    )
    raw_id_fields = ('lead', )

    def get_actions(self, request):
        actions = super(LeadAccountAdmin, self).get_actions(request)
        keys = list(actions.keys())
        for key in keys:
            if key not in self.actions:
                del actions[key]
        return actions

    def get_queryset(self, request):
        queryset = super(LeadAccountAdmin, self).get_queryset(request)
        queryset = queryset.prefetch_related(
            'lead',
            'lead__bundler',
            'lead__raspberry_pi',
            'lead__ec2instance',
        )
        return queryset

    def name(self, obj):
        if obj.note:
            return mark_safe('<span class="has_note" title="{}">{}</span>'.format(
                obj.note,
                obj.lead.name(),
            ))
        return obj.lead.name()

    def lead_link(self, obj):
        lead = obj.lead
        return mark_safe('<a target="_blank" href="{url}?q={q}">{lead}</a>'.format(
            url=reverse('admin:adsrental_lead_changelist'),
            lead=lead.leadid,
            q=lead.leadid,
        ))

    def raspberry_pi_field(self, obj):
        if not obj.lead.raspberry_pi:
            return None

        return mark_safe('<a target="_blank" href="{url}?q={rpid}">{rpid}</a>'.format(
            url=reverse('admin:adsrental_raspberrypi_changelist'),
            rpid=obj.lead.raspberry_pi,
        ))

    def status_field(self, obj):
        title = 'Show changes'
        if obj.ban_reason:
            title = 'Banned for {}'.format(obj.ban_reason)
        return mark_safe('<a target="_blank" href="{url}?q={q}" title="{title}">{status}</a>'.format(
            url=reverse('admin:adsrental_leadchange_changelist'),
            q=obj.lead.leadid,
            title=title,
            status=obj.status if obj.status != LeadAccount.STATUS_BANNED else '{} ({})'.format(obj.status, obj.ban_reason),
        ))

    def online(self, obj):
        return obj.lead.raspberry_pi.online() if obj.lead.raspberry_pi else False

    def first_seen(self, obj):
        if obj.lead.raspberry_pi is None or obj.lead.raspberry_pi.first_seen is None:
            return None

        first_seen = obj.lead.raspberry_pi.get_first_seen()
        return mark_safe(u'<span class="has_note" title="{}">{}</span>'.format(first_seen, naturaltime(first_seen)))

    def last_seen(self, obj):
        if obj.lead.raspberry_pi is None or obj.lead.raspberry_pi.last_seen is None:
            return None

        last_seen = obj.lead.raspberry_pi.get_last_seen()

        return mark_safe(u'<span class="has_note" title="{}">{}</span>'.format(last_seen, naturaltime(last_seen)))

    def last_touch(self, obj):
        if obj.account_type != LeadAccount.ACCOUNT_TYPE_FACEBOOK:
            return None

        return naturaltime(obj.last_touch_date) if obj.last_touch_date else 'Never'

    def touch_count_field(self, obj):
        return obj.touch_count

    def wrong_password_date_field(self, obj):
        if not obj.wrong_password_date:
            return None

        return mark_safe('<span title="{}">{}</span>'.format(
            obj.wrong_password_date,
            naturaltime(obj.wrong_password_date),
        ))

    def security_checkpoint_date_field(self, obj):
        if not obj.security_checkpoint_date:
            return None

        return mark_safe('<span title="{}">{}</span>'.format(
            obj.security_checkpoint_date,
            naturaltime(obj.security_checkpoint_date),
        ))

    def mark_as_qualified(self, request, queryset):
        for lead_account in queryset:
            if lead_account.is_banned():
                messages.warning(request, '{} is {}, skipping'.format(lead_account, lead_account.status))
                continue

            lead_account.qualify(request.user)
            if lead_account.lead.assign_raspberry_pi():
                messages.success(
                    request, '{} has new Raspberry Pi assigned: {}'.format(lead_account, lead_account.lead.raspberry_pi.rpid))

            if lead_account.lead.add_shipstation_order():
                messages.success(
                    request, '{} order created: {}'.format(lead_account, lead_account.lead.shipstation_order_number))
            else:
                messages.info(
                    request, 'Lead {} order already exists: {}. If you want to ship another, clear shipstation_order_number field first'.format(lead_account, lead_account.lead.shipstation_order_number))

    def mark_as_disqualified(self, request, queryset):
        for lead_account in queryset:
            if lead_account.is_banned():
                messages.warning(request, '{} is {}, skipping'.format(lead_account, lead_account.status))
                continue

            lead_account.disqualify(request.user)
            messages.info(request, '{} is disqualified.'.format(lead_account))

    def ban(self, request, queryset):
        if 'do_action' in request.POST:
            form = AdminLeadAccountBanForm(request.POST)
            if form.is_valid():
                reason = form.cleaned_data['reason']
                for lead_account in queryset:
                    lead_account.ban(request.user, reason)
                    messages.info(request, '{} is banned.'.format(lead_account))
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
                messages.info(request, '{} is unbanned.'.format(lead_account))

    def report_wrong_password(self, request, queryset):
        for lead_account in queryset:
            if lead_account.wrong_password_date is None:
                lead_account.wrong_password_date = timezone.now()
                lead_account.save()
                messages.info(request, '{} password is marked as wrong.'.format(lead_account))

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
            form = AdminLeadAccountPasswordForm(initial=dict(
                old_password=lead_account.password,
                new_password=lead_account.password,
            ))

        return render(request, 'admin/action_with_form.html', {
            'action_name': 'report_correct_password',
            'title': 'Set new pasword for {}'.format(lead_account),
            'button': 'Save password',
            'objects': queryset,
            'form': form,
        })


    def report_security_checkpoint(self, request, queryset):
        for lead_account in queryset:
            if lead_account.is_security_checkpoint_reported():
                messages.info(request, '{} security checkpoint is already reported, skipping.'.format(lead_account))
                continue

            lead_account.security_checkpoint_date = timezone.now()
            lead_account.save()
            messages.info(request, '{} security checkpoint reported.'.format(lead_account))

    def report_security_checkpoint_resolved(self, request, queryset):
        for lead_account in queryset:
            if not lead_account.is_security_checkpoint_reported():
                messages.info(request, '{} security checkpoint is not reported, skipping.'.format(lead_account))
                continue

            lead_account.security_checkpoint_date = None
            lead_account.save()
            messages.info(request, '{} security checkpoint reported as resolved.'.format(lead_account))

    def sync_to_adsdb(self, request, queryset):
        for lead_account in queryset:
            result = lead_account.sync_to_adsdb()
            if result:
                messages.info(request, '{} is synced: {}'.format(lead_account, result))
            else:
                messages.warning(request, '{} does not meet conditions to sync.'.format(lead_account))

    def touch(self, request, queryset):
        for lead_account in queryset:
            lead_account.touch()
            messages.info(request, '{} has been touched for {} time.'.format(lead_account, lead_account.touch_count))

    lead_link.short_description = 'Lead'
    lead_link.admin_order_field = 'lead__leadid'

    status_field.short_description = 'Status'
    status_field.admin_order_field = 'status'

    raspberry_pi_field.short_description = 'Raspberry PI'

    wrong_password_date_field.short_description = 'Wrong Password'
    wrong_password_date_field.admin_order_field = 'wrong_password_date'

    security_checkpoint_date_field.short_description = 'Security Checkpoint'
    security_checkpoint_date_field.admin_order_field = 'security_checkpoint_date'

    sync_to_adsdb.short_description = 'DEBUG: Sync to ADSDB'

    mark_as_qualified.short_description = 'Mark as Qualified, Assign RPi, create Shipstation order'

    last_touch.admin_order_field = 'last_touch_date'

    touch_count_field.short_description = 'Touch count'
    touch_count_field.admin_order_field = 'touch_count'

    online.boolean = True
    online.admin_order_field = 'lead__raspberry_pi__last_seen'

    first_seen.empty_value_display = 'Never'
    first_seen.admin_order_field = 'lead__raspberry_pi__first_seen'

    last_seen.empty_value_display = 'Never'
    last_seen.admin_order_field = 'lead__raspberry_pi__last_seen'


class ReadOnlyLeadAccountAdmin(LeadAccountAdmin):
    model = ReadOnlyLeadAccount
    list_display = (
        'id',
        'name',
        'lead_link',
        'raspberry_pi_field',
        'account_type',
        'status',
        'username',
        'password',
        'friends',
        'bundler_paid',
        'last_touch',
        'touch_count_field',
        'adsdb_account_id',
        'wrong_password_date_field',
        'billed',
        'created',
    )

    editable_fields = (
        'note',
    )

    actions = (
        'report_wrong_password',
        'report_correct_password',
        'report_security_checkpoint',
        'report_security_checkpoint_resolved',
    )

    # We cannot call super().get_fields(request, obj) because that method calls
    # get_readonly_fields(request, obj), causing infinite recursion. Ditto for
    # super().get_form(request, obj). So we  assume the default ModelForm.
    def get_readonly_fields(self, request, obj=None):
        fields = self.fields or [f.name for f in self.model._meta.fields]
        fields = list(filter(lambda x: x not in self.editable_fields, fields))
        return fields

    def has_add_permission(self, request):
        return False

    # Allow viewing objects but not actually changing them.
    # def has_change_permission(self, request, obj=None):
    #     return (request.method in ['GET', 'HEAD'] and
    #             super().has_change_permission(request, obj))

    def has_delete_permission(self, request, obj=None):
        return False

    def lead_link(self, obj):
        lead = obj.lead
        return mark_safe('<a target="_blank" href="{url}?q={q}">{lead}</a>'.format(
            url=reverse('admin:adsrental_readonlylead_changelist'),
            lead=lead.leadid,
            q=lead.leadid,
        ))

    def raspberry_pi_field(self, obj):
        if not obj.lead.raspberry_pi:
            return None

        return obj.lead.raspberry_pi

    lead_link.short_description = 'Lead'
    lead_link.admin_order_field = 'lead__leadid'

    raspberry_pi_field.short_description = 'Raspberry Pi'
