
from __future__ import unicode_literals

import html

from django.contrib import admin
from django.shortcuts import render
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

from adsrental.forms import AdminLeadAccountBanForm, AdminPrepareForReshipmentForm, AdminLeadAccountPasswordForm
from adsrental.models.lead import Lead, ReadOnlyLead, ReportProxyLead
from adsrental.models.lead_account import LeadAccount
from adsrental.models.lead_change import LeadChange
from adsrental.admin.list_filters import \
    StatusListFilter, \
    RaspberryPiOnlineListFilter, \
    AccountTypeListFilter, \
    LeadAccountWrongPasswordListFilter, \
    DeliveryDateListFilter, \
    LeadAccountTouchCountListFilter, \
    BundlerListFilter, \
    ShipDateListFilter, \
    LeadAccountSecurityCheckpointListFilter


class LeadAccountInline(admin.StackedInline):
    model = LeadAccount
    max_num = 3
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


class LeadChangeInline(admin.TabularInline):
    model = LeadChange
    max_num = 2
    readonly_fields = (
        'field',
        'value',
        'old_value',
        'created',
        'edited_by',
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class LeadAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }

    model = Lead

    list_display = (
        'name',
        'status_field',
        'links',
        'email_field',
        'phone_field',
        'bundler_field',
        'accounts_field',
        'raspberry_pi_link',
        'tested_field',
        'usps_field',
        'first_seen',
        'last_seen',
        'online',
        'ec2_instance_link',
        'touch_count_field',
        'touch_button',
        'ip_address',
        'fix_button',
        'wrong_password_field',
        'security_checkpoint_field',
        'sync_with_adsdb_field',
        'facebook_billed',
        'google_billed',
    )
    list_filter = (
        StatusListFilter,
        RaspberryPiOnlineListFilter,
        AccountTypeListFilter,
        LeadAccountWrongPasswordListFilter,
        LeadAccountTouchCountListFilter,
        'shipstation_order_status',
        'company',
        'lead_account__bundler_paid',
        ShipDateListFilter,
        DeliveryDateListFilter,
        BundlerListFilter,
        'pi_delivered',
        LeadAccountSecurityCheckpointListFilter,
        'lead_account__charge_back',
        'lead_account__charge_back_billed',
    )
    inlines = (
        # LeadChangeInline,
        LeadAccountInline,
    )
    # list_prefetch_related = ('raspberry_pi', 'ec2instance', 'bundler',)
    # list_prefetch_related = ('lead_accounts', )
    search_fields = (
        'leadid',
        'account_name',
        'first_name',
        'last_name',
        'raspberry_pi__rpid',
        'email',
    )
    actions = (
        # 'update_from_shipstation',
        'mark_facebook_as_qualified',
        'mark_google_as_qualified',
        'mark_amazon_as_qualified',
        'mark_as_disqualified',
        'ban_google_account',
        'unban_google_account',
        'ban_facebook_account',
        'unban_facebook_account',
        'ban_amazon_account',
        'unban_amazon_account',
        'report_wrong_google_password',
        'report_correct_google_password',
        'report_wrong_facebook_password',
        'report_correct_facebook_password',
        'report_wrong_amazon_password',
        'report_correct_amazon_password',
        'report_security_checkpoint_google',
        'report_security_checkpoint_google_resolved',
        'report_security_checkpoint_facebook',
        'report_security_checkpoint_facebook_resolved',
        'report_security_checkpoint_amazon',
        'report_security_checkpoint_amazon_resolved',
        'prepare_for_testing',
        'touch',
        'restart_raspberry_pi',
        'sync_to_adsdb_facebook',
        'sync_to_adsdb_google',
    )
    readonly_fields = (
        'created',
        'updated',
        'account_name',
        'status',
        'old_status',
        'shipstation_order_number',
        'raspberry_pi',
    )
    exclude = ('tracking_info', )
    raw_id_fields = ('raspberry_pi', )

    def __init__(self, *args, **kwargs):
        self._request = None
        super(LeadAdmin, self).__init__(*args, **kwargs)

    def get_list_display(self, request):
        self._request = request
        list_display = super(LeadAdmin, self).get_list_display(request)
        return list_display

    def get_queryset(self, request):
        queryset = super(LeadAdmin, self).get_queryset(request)
        queryset = queryset.prefetch_related(
            'bundler',
            'ec2instance',
            'raspberry_pi',
            'lead_accounts',
        )
        return queryset

    def get_actions(self, request):
        actions = super(LeadAdmin, self).get_actions(request)
        keys = list(actions.keys())
        for key in keys:
            if key not in self.actions:
                del actions[key]
        return actions

    def id_field(self, obj):
        return obj.leadid

    def name(self, obj):
        if obj.note:
            return mark_safe('<span class="has_note" title="{}">{}</span>'.format(
                html.escape(obj.note),
                obj.name(),
            ))
        return obj.name()

    def usps_field(self, obj):
        if obj.pi_delivered:
            return mark_safe('<span class="has_note" title="{}">{}</span>'.format(
                html.escape(obj.usps_tracking_code or 'n/a'),
                'Delivered',
            ))

        if not obj.shipstation_order_status:
            return None

        return mark_safe('<span class="has_note" title="{}">{}</span>'.format(
            html.escape(obj.usps_tracking_code or 'n/a'),
            obj.get_shipstation_order_status_display(),
        ))

    def status_field(self, obj):
        title = 'Show changes'
        return mark_safe('<a target="_blank" href="{url}?q={q}" title="{title}">{status}</a>'.format(
            url=reverse('admin:adsrental_leadchange_changelist'),
            q=obj.email,
            title=title,
            status=obj.status,
        ))

    def ip_address(self, obj):
        return obj.raspberry_pi and obj.raspberry_pi.ip_address

    def bundler_field(self, obj):
        if obj.bundler:
            return mark_safe('<a target="_blank" href="{url}?q={q}" title="{title}">{text}</a>'.format(
                url=reverse('admin:adsrental_bundler_changelist'),
                q=obj.bundler.email,
                title=obj.bundler.utm_source,
                text=obj.bundler,
            ))

        return obj.utm_source

    def email_field(self, obj):
        return obj.email

    def phone_field(self, obj):
        return obj.get_phone_formatted()

    def facebook_billed(self, obj):
        for lead_account in obj.lead_accounts.all():
            if lead_account.active and lead_account.account_type == LeadAccount.ACCOUNT_TYPE_FACEBOOK:
                return lead_account.billed

        return False

    def google_billed(self, obj):
        for lead_account in obj.lead_accounts.all():
            if lead_account.active and lead_account.account_type == LeadAccount.ACCOUNT_TYPE_GOOGLE:
                return lead_account.billed

        return False

    def last_touch(self, obj):
        for lead_account in obj.lead_accounts.all():
            if lead_account.account_type == LeadAccount.ACCOUNT_TYPE_FACEBOOK:
                return naturaltime(lead_account.last_touch_date) if lead_account.last_touch_date else 'Never'

        return None

    def touch_count_field(self, obj):
        for lead_account in obj.lead_accounts.all():
            if lead_account.account_type == LeadAccount.ACCOUNT_TYPE_FACEBOOK:
                return lead_account.touch_count

        return None

    def online(self, obj):
        return obj.raspberry_pi.online() if obj.raspberry_pi else False

    def tested_field(self, obj):
        if obj.raspberry_pi and obj.raspberry_pi.first_tested:
            return mark_safe('<img src="/static/admin/img/icon-yes.svg" title="{}" alt="True">'.format(
                naturaltime(obj.raspberry_pi.first_tested),
            ))

        return None

    def first_seen(self, obj):
        if obj.raspberry_pi is None or obj.raspberry_pi.first_seen is None:
            return None

        first_seen = obj.raspberry_pi.get_first_seen()
        return mark_safe(u'<span class="has_note" title="{}">{}</span>'.format(first_seen, first_seen.strftime(settings.HUMAN_DATE_FORMAT)))

    def last_seen(self, obj):
        if obj.raspberry_pi is None or obj.raspberry_pi.last_seen is None:
            return None

        last_seen = obj.raspberry_pi.get_last_seen()

        return mark_safe(u'<span class="has_note" title="{}">{}</span>'.format(last_seen, naturaltime(last_seen)))

    def wrong_password_field(self, obj):
        for lead_account in obj.lead_accounts.all():
            if not lead_account.wrong_password_date:
                continue

            return mark_safe('<span class="has_note" title="{}">{}</span>'.format(
                lead_account.wrong_password_date,
                naturaltime(lead_account.wrong_password_date),
            ))

        return None

    def security_checkpoint_field(self, obj):
        for lead_account in obj.lead_accounts.all():
            if not lead_account.security_checkpoint_date:
                continue

            return mark_safe('<span class="has_note" title="{}">{}</span>'.format(
                lead_account.security_checkpoint_date,
                naturaltime(lead_account.security_checkpoint_date),
            ))

        return None

    def raspberry_pi_link(self, obj):
        if not obj.raspberry_pi:
            return None

        return mark_safe('<a target="_blank" href="{url}?q={rpid}">{rpid}</a>'.format(
            url=reverse('admin:adsrental_raspberrypi_changelist'),
            rpid=obj.raspberry_pi,
        ))

    def links(self, obj):
        result = []
        if obj.raspberry_pi:
            result.append('<a target="_blank" href="{log_url}">Logs</a>'.format(log_url=reverse('show_log_dir', kwargs={'rpid': obj.raspberry_pi.rpid})))
            result.append('<a target="_blank" href="{url}?rpid={rpid}">RDP</a>'.format(
                url=reverse('rdp_connect'),
                rpid=obj.raspberry_pi.rpid,
            ))
            result.append('<a href="{config_url}">pi.conf</a>'.format(config_url=reverse('farming_pi_config', kwargs={
                'rpid': obj.raspberry_pi.rpid,
            })))

        result.append('<a href="{url}">Fix address</a>'.format(
            url=reverse('dashboard_change_address', kwargs={'lead_id': obj.leadid})
        ))

        result.append('<a target="_blank" href="{url}?q={q}">History</a>'.format(
            url=reverse('admin:adsrental_leadchange_changelist'),
            q=obj.leadid,
        ))

        if obj.photo_id:
            result.append('<a href="{url}">Photo ID</a>'.format(
                url=reverse('dashboard_photo', kwargs={'lead_id': obj.leadid}),
            ))

        result.append('<a href="{url}?q={search}">Checks</a>'.format(
            url=reverse('admin:adsrental_leadhistorymonth_changelist'),
            search=obj.email,
        ))

        return mark_safe(', '.join(result))

    def ec2_instance_link(self, obj):
        result = []
        ec2_instance = obj.get_ec2_instance()
        if ec2_instance:
            result.append('<a target="_blank" href="{url}?q={q}">{ec2_instance}</a>'.format(
                url=reverse('admin:adsrental_ec2instance_changelist'),
                ec2_instance=ec2_instance.hostname or ec2_instance.status.capitalize(),
                q=ec2_instance.instance_id,
            ))

        return mark_safe('\n'.join(result))

    def accounts_field(self, obj):
        result = []
        for lead_account in obj.lead_accounts.all():
            result.append('<a href="{}?q={}&account_type__exact={}">{} ({})</a>'.format(
                reverse('admin:adsrental_leadaccount_changelist'),
                obj.email,
                lead_account.account_type,
                lead_account.account_type,
                lead_account.status,
            ))

        return mark_safe(', '.join(result))

    def sync_with_adsdb_field(self, obj):
        for lead_account in obj.lead_accounts.all():
            if lead_account.active and lead_account.sync_with_adsdb:
                return True

        return False

    def update_from_shipstation(self, request, queryset):
        for lead in queryset:
            lead.update_from_shipstation()

    def mark_google_as_qualified(self, request, queryset):
        for lead in queryset:
            for lead_account in lead.lead_accounts.filter(account_type=LeadAccount.ACCOUNT_TYPE_GOOGLE):
                if lead_account.is_banned():
                    messages.warning(request, 'Lead Account {} is {}, skipping'.format(lead_account, lead_account.status))
                    continue

                lead_account.qualify(request.user)
                if lead_account.lead.assign_raspberry_pi():
                    messages.success(
                        request, 'Lead Account {} has new Raspberry Pi assigned: {}'.format(lead_account, lead_account.lead.raspberry_pi.rpid))

                if lead_account.lead.add_shipstation_order():
                    messages.success(
                        request, '{} order created: {}'.format(lead_account, lead_account.lead.shipstation_order_number))
                else:
                    messages.info(
                        request, 'Lead {} order already exists: {}.'.format(lead_account, lead_account.lead.shipstation_order_number))

    def mark_facebook_as_qualified(self, request, queryset):
        for lead in queryset:
            for lead_account in lead.lead_accounts.filter(account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK):
                if lead_account.is_banned():
                    messages.warning(request, 'Lead Account {} is {}, skipping'.format(lead_account, lead_account.status))
                    continue

                lead_account.qualify(request.user)
                if lead_account.lead.assign_raspberry_pi():
                    messages.success(
                        request, 'Lead Account {} has new Raspberry Pi assigned: {}'.format(lead_account, lead_account.lead.raspberry_pi.rpid))

                if lead_account.lead.add_shipstation_order():
                    messages.success(
                        request, '{} order created: {}'.format(lead_account, lead_account.lead.shipstation_order_number))
                else:
                    messages.info(
                        request, 'Lead {} order already exists: {}.'.format(lead_account, lead_account.lead.shipstation_order_number))

    def mark_amazon_as_qualified(self, request, queryset):
        for lead in queryset:
            for lead_account in lead.lead_accounts.filter(account_type=LeadAccount.ACCOUNT_TYPE_AMAZON):
                if lead_account.is_banned():
                    messages.warning(request, 'Lead Account {} is {}, skipping'.format(lead_account, lead_account.status))
                    continue

                lead_account.qualify(request.user)
                if lead_account.lead.assign_raspberry_pi():
                    messages.success(
                        request, 'Lead Account {} has new Raspberry Pi assigned: {}'.format(lead_account, lead_account.lead.raspberry_pi.rpid))

                if lead_account.lead.add_shipstation_order():
                    messages.success(
                        request, '{} order created: {}'.format(lead_account, lead_account.lead.shipstation_order_number))
                else:
                    messages.info(
                        request, 'Lead {} order already exists: {}.'.format(lead_account, lead_account.lead.shipstation_order_number))

    def mark_as_disqualified(self, request, queryset):
        for lead in queryset:
            for lead_account in lead.lead_accounts.all():
                if lead_account.is_banned():
                    messages.warning(request, 'Lead Account {} is {}, skipping'.format(lead_account, lead_account.status))
                    continue

                lead_account.disqualify(request.user)
                messages.info(request, 'Lead Account {} is disqualified.'.format(lead_account))

    def ban_google_account(self, request, queryset):
        if 'do_action' in request.POST:
            form = AdminLeadAccountBanForm(request.POST)
            if form.is_valid():
                reason = form.cleaned_data['reason']
                for lead in queryset:
                    for lead_account in lead.lead_accounts.filter(account_type=LeadAccount.ACCOUNT_TYPE_GOOGLE):
                        lead_account.ban(request.user, reason)
                        messages.info(request, '{} is banned.'.format(lead_account))
                return None
        else:
            form = AdminLeadAccountBanForm()

        return render(request, 'admin/action_with_form.html', {
            'action_name': 'ban_google_account',
            'title': 'Choose reason to ban Google account',
            'button': 'Ban',
            'objects': queryset,
            'form': form,
        })

    def unban_google_account(self, request, queryset):
        for lead in queryset:
            for lead_account in lead.lead_accounts.filter(account_type=LeadAccount.ACCOUNT_TYPE_GOOGLE):
                if lead_account.unban(request.user):
                    messages.info(request, '{} is unbanned.'.format(lead_account))

    def ban_facebook_account(self, request, queryset):
        if 'do_action' in request.POST:
            form = AdminLeadAccountBanForm(request.POST)
            if form.is_valid():
                reason = form.cleaned_data['reason']
                for lead in queryset:
                    for lead_account in lead.lead_accounts.filter(account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK):
                        lead_account.ban(request.user, reason)
                        messages.info(request, '{} is banned.'.format(lead_account))
                return None
        else:
            form = AdminLeadAccountBanForm()

        return render(request, 'admin/action_with_form.html', {
            'action_name': 'ban_facebook_account',
            'title': 'Choose reason to ban Facebook account',
            'button': 'Ban',
            'objects': queryset,
            'form': form,
        })

    def unban_facebook_account(self, request, queryset):
        for lead in queryset:
            for lead_account in lead.lead_accounts.filter(account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK):
                if lead_account.unban(request.user):
                    messages.info(request, '{} is unbanned.'.format(lead_account))

    def ban_amazon_account(self, request, queryset):
        if 'do_action' in request.POST:
            form = AdminLeadAccountBanForm(request.POST)
            if form.is_valid():
                reason = form.cleaned_data['reason']
                for lead in queryset:
                    for lead_account in lead.lead_accounts.filter(account_type=LeadAccount.ACCOUNT_TYPE_AMAZON):
                        lead_account.ban(request.user, reason)
                        messages.info(request, '{} is banned.'.format(lead_account))
                return None
        else:
            form = AdminLeadAccountBanForm()

        return render(request, 'admin/action_with_form.html', {
            'action_name': 'ban_amazon_account',
            'title': 'Choose reason to ban Amazon account',
            'button': 'Ban',
            'objects': queryset,
            'form': form,
        })

    def unban_amazon_account(self, request, queryset):
        for lead in queryset:
            for lead_account in lead.lead_accounts.filter(account_type=LeadAccount.ACCOUNT_TYPE_AMAZON):
                if lead_account.unban(request.user):
                    messages.info(request, '{} is unbanned.'.format(lead_account))

    def restart_raspberry_pi(self, request, queryset):
        for lead in queryset:
            if not lead.raspberry_pi:
                messages.warning(request, 'Lead {} does not haave RaspberryPi assigned, skipping'.format(lead.email))
                continue

            lead.raspberry_pi.restart_required = True
            lead.raspberry_pi.save()
            lead.clear_ping_cache()
            messages.info(request, 'Lead {} RPi restart successfully requested. RPi and tunnel should be online in two minutes.'.format(lead.email))

    def prepare_for_testing(self, request, queryset):
        if 'do_action' in request.POST:
            form = AdminPrepareForReshipmentForm(request.POST)
            if form.is_valid():
                rpids = form.cleaned_data['rpids']
                queryset = Lead.objects.filter(raspberry_pi__rpid__in=rpids)
                for lead in queryset:
                    if lead.is_banned():
                        lead.unban(request.user)
                        messages.info(request, 'Lead {} is unbanned.'.format(lead.email))

                    if lead.raspberry_pi.first_tested:
                        lead.prepare_for_reshipment(request.user)
                        messages.info(request, 'RPID {} is prepared for testing.'.format(lead.raspberry_pi.rpid))

                    messages.success(request, 'RPID {} is ready to be tested.'.format(lead.raspberry_pi.rpid))
                return None
        else:
            rpids = [i.raspberry_pi.rpid for i in queryset if i.raspberry_pi]
            form = AdminPrepareForReshipmentForm(initial=dict(
                rpids='\n'.join(rpids),
            ))

        return render(request, 'admin/action_with_form.html', {
            'action_name': 'prepare_for_testing',
            'title': 'Prepare for reshipment following leads',
            'button': 'Prepare for reshipment',
            'objects': queryset,
            'form': form,
        })

    def report_security_checkpoint_google(self, request, queryset):
        for lead in queryset:
            lead_account = lead.lead_accounts.filter(account_type=LeadAccount.ACCOUNT_TYPE_GOOGLE, active=True).first()

            if not lead_account:
                messages.info(request, 'Lead {} has no active google account.'.format(lead.email))
                continue

            if lead_account.is_security_checkpoint_reported():
                messages.info(request, 'Lead Account {} security checkpoint is already reported, skipping.'.format(lead_account))
                continue

            lead_account.security_checkpoint_date = timezone.now()
            lead_account.save()
            messages.info(request, 'Lead Account {} security checkpoint reported.'.format(lead_account))

    def report_security_checkpoint_google_resolved(self, request, queryset):
        for lead in queryset:
            lead_account = lead.lead_accounts.filter(account_type=LeadAccount.ACCOUNT_TYPE_GOOGLE, active=True).first()

            if not lead_account:
                messages.info(request, 'Lead {} has no active google account.'.format(lead.email))
                continue

            if not lead_account.is_security_checkpoint_reported():
                messages.info(request, 'Lead Account {} security checkpoint is not reported, skipping.'.format(lead_account))
                continue

            lead_account.security_checkpoint_date = None
            lead_account.save()
            messages.info(request, 'Lead Account {} security checkpoint reported as resolved.'.format(lead_account))

    def report_security_checkpoint_facebook(self, request, queryset):
        for lead in queryset:
            lead_account = lead.lead_accounts.filter(account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK, active=True).first()

            if not lead_account:
                messages.info(request, 'Lead {} has no active facebook account.'.format(lead.email))
                continue

            if lead_account.is_security_checkpoint_reported():
                messages.info(request, 'Lead Account {} security checkpoint is already reported, skipping.'.format(lead_account))
                continue

            lead_account.security_checkpoint_date = timezone.now()
            lead_account.save()
            messages.info(request, 'Lead Account {} security checkpoint reported.'.format(lead_account))

    def report_security_checkpoint_facebook_resolved(self, request, queryset):
        for lead in queryset:
            lead_account = lead.lead_accounts.filter(account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK, active=True).first()

            if not lead_account:
                messages.info(request, 'Lead {} has no active facebook account.'.format(lead.email))
                continue

            if not lead_account.is_security_checkpoint_reported():
                messages.info(request, 'Lead Account {} security checkpoint is not reported, skipping.'.format(lead_account))
                continue

            lead_account.security_checkpoint_date = None
            lead_account.save()
            messages.info(request, 'Lead Account {} security checkpoint reported as resolved.'.format(lead_account))

    def report_security_checkpoint_amazon(self, request, queryset):
        for lead in queryset:
            lead_account = lead.lead_accounts.filter(account_type=LeadAccount.ACCOUNT_TYPE_AMAZON, active=True).first()

            if not lead_account:
                messages.info(request, 'Lead {} has no active Amazon account.'.format(lead.email))
                continue

            if lead_account.is_security_checkpoint_reported():
                messages.info(request, 'Lead Account {} security checkpoint is already reported, skipping.'.format(lead_account))
                continue

            lead_account.security_checkpoint_date = timezone.now()
            lead_account.save()
            messages.info(request, 'Lead Account {} security checkpoint reported.'.format(lead_account))

    def report_security_checkpoint_amazon_resolved(self, request, queryset):
        for lead in queryset:
            lead_account = lead.lead_accounts.filter(account_type=LeadAccount.ACCOUNT_TYPE_AMAZON, active=True).first()

            if not lead_account:
                messages.info(request, 'Lead {} has no active Amazon account.'.format(lead.email))
                continue

            if not lead_account.is_security_checkpoint_reported():
                messages.info(request, 'Lead Account {} security checkpoint is not reported, skipping.'.format(lead_account))
                continue

            lead_account.security_checkpoint_date = None
            lead_account.save()
            messages.info(request, 'Lead Account {} security checkpoint reported as resolved.'.format(lead_account))

    def report_wrong_google_password(self, request, queryset):
        for lead in queryset:
            lead_account = lead.lead_accounts.filter(account_type=LeadAccount.ACCOUNT_TYPE_GOOGLE, active=True).first()

            if not lead_account:
                messages.info(request, 'Lead {} has no active google account.'.format(lead.email))
                continue

            if lead_account.is_wrong_password():
                messages.info(request, 'Lead Account {} was already marked as wrong, skipping.'.format(lead_account))
                continue

            lead_account.mark_wrong_password(request.user)
            messages.info(request, 'Lead Account {} password is marked as wrong.'.format(lead_account))

    @staticmethod
    def report_correct_google_password(instance, request, queryset):
        if queryset.count() != 1:
            messages.error(request, 'Only one lead can be selected.')
            return None

        lead = queryset.first()

        lead_account = lead.lead_accounts.filter(account_type=LeadAccount.ACCOUNT_TYPE_GOOGLE, active=True).first()
        if not lead_account:
            messages.error(request, 'Lead has no active google account.')
            return None

        if not lead_account.is_wrong_password():
            messages.info(request, 'Lead Account {} is not marked as wrong, skipping.'.format(lead_account))
            return None

        if 'do_action' in request.POST:
            form = AdminLeadAccountPasswordForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password']
                lead_account.set_correct_password(new_password, request.user)
                messages.info(request, 'Lead Account {} password is marked as correct.'.format(lead_account))
                return None
        else:
            form = AdminLeadAccountPasswordForm(initial=dict(
                old_password=lead_account.password,
                new_password=lead_account.password,
            ))

        return render(request, 'admin/action_with_form.html', {
            'action_name': 'report_correct_google_password',
            'title': 'Set new pasword for {}'.format(lead_account),
            'button': 'Save password',
            'objects': queryset,
            'form': form,
        })

    def report_wrong_facebook_password(self, request, queryset):
        for lead in queryset:
            lead_account = lead.lead_accounts.filter(account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK, active=True).first()

            if not lead_account:
                messages.error(request, 'Lead {} has no active facebook account.'.format(lead.email))
                continue

            if lead_account.is_wrong_password():
                messages.info(request, 'Lead Account {} was already marked as wrong, skipping.'.format(lead_account))
                continue

            lead_account.mark_wrong_password(request.user)
            messages.info(request, 'Lead Account {} password is marked as wrong.'.format(lead_account))

    @staticmethod
    def report_correct_facebook_password(instance, request, queryset):
        if queryset.count() != 1:
            messages.error(request, 'Only one lead can be selected.')
            return None

        lead = queryset.first()

        lead_account = lead.lead_accounts.filter(account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK, active=True).first()
        if not lead_account:
            messages.error(request, 'Lead has no active facebook account.')
            return None

        if not lead_account.is_wrong_password():
            messages.info(request, 'Lead Account {} is not marked as wrong, skipping.'.format(lead_account))
            return None

        if 'do_action' in request.POST:
            form = AdminLeadAccountPasswordForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password']
                lead_account.set_correct_password(new_password, request.user)
                messages.info(request, 'Lead Account {} password is marked as correct.'.format(lead_account))
                return None
        else:
            form = AdminLeadAccountPasswordForm(initial=dict(
                old_password=lead_account.password,
                new_password=lead_account.password,
            ))

        return render(request, 'admin/action_with_form.html', {
            'action_name': 'report_correct_facebook_password',
            'title': 'Set new pasword for {}'.format(lead_account),
            'button': 'Save password',
            'objects': queryset,
            'form': form,
        })

    def report_wrong_amazon_password(self, request, queryset):
        for lead in queryset:
            lead_account = lead.lead_accounts.filter(account_type=LeadAccount.ACCOUNT_TYPE_AMAZON, active=True).first()

            if not lead_account:
                messages.error(request, 'Lead {} has no active Amazon account.'.format(lead.email))
                continue

            if lead_account.is_wrong_password():
                messages.info(request, 'Lead Account {} was already marked as wrong, skipping.'.format(lead_account))
                continue

            lead_account.mark_wrong_password(request.user)
            messages.info(request, 'Lead Account {} password is marked as wrong.'.format(lead_account))

    @staticmethod
    def report_correct_amazon_password(instance, request, queryset):
        if queryset.count() != 1:
            messages.error(request, 'Only one lead can be selected.')
            return None

        lead = queryset.first()

        lead_account = lead.lead_accounts.filter(account_type=LeadAccount.ACCOUNT_TYPE_AMAZON, active=True).first()
        if not lead_account:
            messages.error(request, 'Lead has no active Amazon account.')
            return None

        if not lead_account.is_wrong_password():
            messages.info(request, 'Lead Account {} is not marked as wrong, skipping.'.format(lead_account))
            return None

        if 'do_action' in request.POST:
            form = AdminLeadAccountPasswordForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password']
                lead_account.set_correct_password(new_password, request.user)
                messages.info(request, 'Lead Account {} password is marked as correct.'.format(lead_account))
                return None
        else:
            form = AdminLeadAccountPasswordForm(initial=dict(
                old_password=lead_account.password,
                new_password=lead_account.password,
            ))

        return render(request, 'admin/action_with_form.html', {
            'action_name': 'report_correct_amazon_password',
            'title': 'Set new pasword for {}'.format(lead_account),
            'button': 'Save password',
            'objects': queryset,
            'form': form,
        })

    @staticmethod
    def touch(instance, request, queryset):
        for lead in queryset:
            for lead_account in lead.lead_accounts.filter(active=True, account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK):
                lead_account.touch()
                messages.info(request, '{} has been touched for {} time.'.format(lead_account, lead_account.touch_count))

    def sync_to_adsdb_facebook(self, request, queryset):
        for lead in queryset:
            for lead_account in lead.lead_accounts.filter(active=True, account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK):
                result = lead_account.sync_to_adsdb()
                if result:
                    messages.info(request, '{} is synced: {}'.format(lead_account, result))
                else:
                    messages.warning(request, '{} does not meet conditions to sync.'.format(lead_account))

    def sync_to_adsdb_google(self, request, queryset):
        for lead in queryset:
            for lead_account in lead.lead_accounts.filter(active=True, account_type=LeadAccount.ACCOUNT_TYPE_GOOGLE):
                result = lead_account.sync_to_adsdb()
                if result:
                    messages.info(request, '{} is synced: {}'.format(lead_account, result))
                else:
                    messages.warning(request, '{} does not meet conditions to sync.'.format(lead_account))

    def touch_button(self, obj):
        row_actions = [
            {
                'label': 'Touch',
                'action': 'touch',
                'enabled': [i for i in obj.lead_accounts.all() if i.account_type == i.ACCOUNT_TYPE_FACEBOOK],
            },
        ]

        return mark_safe(render_to_string('django_admin_row_actions/dropdown.html', request=self._request, context=dict(
            obj=obj,
            items=row_actions,
            model_name='LeadAdmin',
        )))

    def fix_button(self, obj):
        row_actions = [
            {
                'label': 'Fix Facebook PW',
                'action': 'report_correct_facebook_password',
                'enabled': obj.is_wrong_password_facebook(),
            },
            {
                'label': 'Fix Google PW',
                'action': 'report_correct_google_password',
                'enabled': obj.is_wrong_password_google(),
            },
        ]

        return mark_safe(render_to_string('django_admin_row_actions/dropdown.html', request=self._request, context=dict(
            obj=obj,
            items=row_actions,
            model_name='LeadAdmin',
        )))

    google_billed.boolean = True
    google_billed.admin_order_field = 'lead_account__billed'

    facebook_billed.boolean = True
    facebook_billed.admin_order_field = 'lead_account__billed'

    status_field.short_description = 'Status'
    status_field.admin_order_field = 'status'

    wrong_password_field.short_description = 'Wrong Password'
    wrong_password_field.admin_order_field = 'lead_account__wrong_password_date'

    security_checkpoint_field.short_description = 'Security Checkpoint'
    security_checkpoint_field.admin_order_field = 'lead_account__security_checkpoint_date'

    tested_field.short_description = 'Tested'

    last_touch.admin_order_field = 'lead_account__last_touch_date'
    touch_count_field.short_description = 'Touch count'
    touch_count_field.admin_order_field = 'lead_account__touch_count'

    id_field.short_description = 'ID'

    mark_facebook_as_qualified.short_description = 'Mark Facebook account as Qualified'
    mark_google_as_qualified.short_description = 'Mark Google account as Qualified'

    ec2_instance_link.short_description = 'EC2 instance'

    email_field.short_description = 'Email'
    email_field.admin_order_field = 'email'

    online.boolean = True
    online.admin_order_field = 'raspberry_pi__last_seen'

    accounts_field.short_description = 'Accounts'

    raspberry_pi_link.short_description = 'Raspberry PI'

    first_seen.empty_value_display = 'Never'
    first_seen.admin_order_field = 'raspberry_pi__first_seen'

    last_seen.empty_value_display = 'Never'
    last_seen.admin_order_field = 'raspberry_pi__last_seen'

    bundler_field.short_description = 'Bundler'
    bundler_field.admin_order_field = 'utm_source'

    name.admin_order_field = 'first_name'

    phone_field.short_description = 'Phone'
    phone_field.admin_order_field = 'phone'

    sync_with_adsdb_field.short_description = 'Sunc with adsdb'
    sync_with_adsdb_field.boolean = True

    touch_button.short_description = ' '
    fix_button.short_description = ' '

    usps_field.short_description = 'USPS'
    usps_field.admin_order_field = 'shipstation_order_status'


class ReportLeadAdmin(LeadAdmin):
    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }

    model = ReportProxyLead
    # admin_caching_enabled = True
    list_per_page = 500
    list_display = (
        'name',
        'status_field',
        'links',
        'email_field',
        'phone_field',
        'bundler_field',
        'accounts_field',
        'raspberry_pi_link',
        'tested_field',
        'usps_field',
        'first_seen',
        'last_seen',
        'online',
        'ec2_instance_link',
        'last_touch',
        'touch_count_field',
        'touch_button',
        'ip_address',
        'fix_button',
        'wrong_password_field',
        'security_checkpoint_field',
        'sync_with_adsdb_field',
        'facebook_billed',
        'google_billed',
    )


class ReadOnlyLeadAdmin(LeadAdmin):
    model = ReadOnlyLead

    list_display = (
        'name',
        'status',
        'email_field',
        'accounts_field',
        'links',
        'last_touch',
        'touch_count_field',
        'first_seen',
        'last_seen',
        'ec2_hostname',
        'raspberry_pi',
        'online',
        'wrong_password_field',
        'security_checkpoint_field',
        'fix_button',
    )

    editable_fields = (
        'note',
    )

    actions = (
        # 'update_from_shipstation',
        # 'mark_facebook_as_qualified',
        # 'mark_google_as_qualified',
        # 'mark_as_disqualified',
        # 'ban_google_account',
        # 'unban_google_account',
        # 'ban_facebook_account',
        # 'unban_facebook_account',
        'report_wrong_google_password',
        'report_correct_google_password',
        'report_wrong_facebook_password',
        'report_correct_facebook_password',
        'report_security_checkpoint_google',
        'report_security_checkpoint_google_resolved',
        'report_security_checkpoint_facebook',
        'report_security_checkpoint_facebook_resolved',
        # 'prepare_for_testing',
        # 'touch',
        # 'restart_raspberry_pi',
        # 'sync_to_adsdb',
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

    def ec2_hostname(self, obj):
        ec2_instance = obj.get_ec2_instance()
        return ec2_instance and ec2_instance.hostname

    def accounts_field(self, obj):
        result = []
        for lead_account in obj.lead_accounts.all():
            result.append('<a href="{}?q={}">{}</a>'.format(
                reverse('admin:adsrental_readonlyleadaccount_changelist'),
                lead_account.username,
                lead_account,
            ))

        return mark_safe(', '.join(result))

    accounts_field.short_description = 'Accounts'
