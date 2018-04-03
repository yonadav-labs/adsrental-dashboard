
from __future__ import unicode_literals

from django.contrib import admin
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils.safestring import mark_safe

from adsrental.forms import AdminLeadAccountBanForm, AdminPrepareForReshipmentForm, AdminLeadAccountPasswordForm
from adsrental.models.lead import Lead, ReadOnlyLead
from adsrental.models.lead_account import LeadAccount
from adsrental.models.ec2_instance import EC2Instance
from adsrental.admin.list_filters import StatusListFilter, RaspberryPiOnlineListFilter, AccountTypeListFilter, LeadAccountWrongPasswordListFilter, RaspberryPiFirstSeenListFilter, TouchCountListFilter, BundlerListFilter, ShipDateListFilter, QualifiedDateListFilter


class LeadAccountInline(admin.StackedInline):
    model = LeadAccount
    max_num = 2
    readonly_fields = (
        'created',
        'updated',
        'status',
        'old_status',
        'wrong_password_date',
        'qualified_date',
    )


class LeadAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }

    model = Lead
    list_display = (
        # 'id_field',
        'name',
        'status_field',
        'email_field',
        'phone_field',
        'bundler_field',
        'accounts_field',
        'links',
        'tested_field',
        'last_touch',
        'first_seen',
        'last_seen',
        'ec2_instance_link',
        'raspberry_pi_link',
        'ip_address',
        'usps_tracking_code',
        'online',
        'wrong_password_field',
        'pi_delivered',
        'bundler_paid_field',
    )
    list_filter = (
        StatusListFilter,
        RaspberryPiOnlineListFilter,
        AccountTypeListFilter,
        LeadAccountWrongPasswordListFilter,
        TouchCountListFilter,
        'company',
        'lead_account__bundler_paid',
        ShipDateListFilter,
        QualifiedDateListFilter,
        RaspberryPiFirstSeenListFilter,
        BundlerListFilter,
        'pi_delivered',
    )
    inlines = (
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
        'mark_as_qualified',
        'mark_as_disqualified',
        'ban_google_account',
        'unban_google_account',
        'ban_facebook_account',
        'unban_facebook_account',
        'report_wrong_google_password',
        'report_correct_google_password',
        'report_wrong_facebook_password',
        'report_correct_facebook_password',
        'prepare_for_testing',
        'touch',
        'restart_raspberry_pi',
        'sync_to_adsdb',
    )
    readonly_fields = (
        'created',
        'updated',
        'status',
        'old_status',
    )
    exclude = ('tracking_info', )
    raw_id_fields = ('raspberry_pi', )


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
                obj.note,
                obj.name(),
            ))
        return obj.name()

    def status_field(self, obj):
        title = 'Show changes'
        return mark_safe('<a target="_blank" href="{url}?q={q}" title="{title}">{status}</a>'.format(
            url=reverse('admin:adsrental_leadchange_changelist'),
            q=obj.leadid,
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

    def last_touch(self, obj):
        return mark_safe('<span title="Touched {} times">{}</span>'.format(
            obj.touch_count,
            naturaltime(obj.last_touch_date) if obj.last_touch_date else 'Never',
        ))

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
        return mark_safe(u'<span title="{}">{}</span>'.format(first_seen, naturaltime(first_seen)))

    def last_seen(self, obj):
        if obj.raspberry_pi is None or obj.raspberry_pi.last_seen is None:
            return None

        last_seen = obj.raspberry_pi.get_last_seen()

        return mark_safe(u'<span title="{}">{}</span>'.format(last_seen, naturaltime(last_seen)))

    def wrong_password_field(self, obj):
        for lead_account in obj.lead_accounts.all():
            if not lead_account.wrong_password_date:
                continue

            return mark_safe('<span title="{}">{}</span>'.format(
                lead_account.wrong_password_date,
                naturaltime(lead_account.wrong_password_date),
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
            result.append('<a href="{rdp_url}">RDP</a>'.format(rdp_url=reverse('rdp', kwargs={'rpid': obj.raspberry_pi.rpid})))
            result.append('<a href="{config_url}">pi.conf</a>'.format(config_url=reverse('farming_pi_config', kwargs={
                'rpid': obj.raspberry_pi.rpid,
            })))

        return mark_safe(', '.join(result))

    def ec2_instance_link(self, obj):
        result = []
        ec2_instance = obj.get_ec2_instance()
        if ec2_instance:
            result.append('<a target="_blank" href="{url}?q={q}">{ec2_instance}</a>'.format(
                url=reverse('admin:adsrental_ec2instance_changelist'),
                ec2_instance=ec2_instance,
                q=ec2_instance.instance_id,
            ))

        return mark_safe('\n'.join(result))

    def accounts_field(self, obj):
        result = []
        for lead_account in obj.lead_accounts.all():
            result.append('<a href="{}?q={}">{}</a>'.format(
                reverse('admin:adsrental_leadaccount_changelist'),
                lead_account.username,
                lead_account,
            ))

        return mark_safe(', '.join(result))

    def bundler_paid_field(self, obj):
        for lead_account in obj.lead_accounts.all():
            if lead_account.active and lead_account.bundler_paid:
                return True

        return False

    def update_from_shipstation(self, request, queryset):
        for lead in queryset:
            lead.update_from_shipstation()


    def mark_as_qualified(self, request, queryset):
        for lead in queryset:
            for lead_account in lead.lead_accounts.all():
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
                    EC2Instance.launch_for_lead(lead_account.lead)
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
                    EC2Instance.launch_for_lead(lead_account.lead)
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

    def report_wrong_google_password(self, request, queryset):
        for lead in queryset:
            lead_account = lead.lead_accounts.filter(account_type=LeadAccount.ACCOUNT_TYPE_GOOGLE, active=True).first()

            if not lead_account:
                messages.info(request, 'Lead {} has no active google account.'.format(lead.email))
                continue

            if lead_account.is_wrong_password():
                messages.info(request, 'Lead Account {} was already marked as wrong, skipping.'.format(lead_account))
                continue

            lead_account.wrong_password_date = timezone.now()
            lead_account.save()
            messages.info(request, 'Lead Account {} password is marked as wrong.'.format(lead_account))

    def report_correct_google_password(self, request, queryset):
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
                lead_account.password = new_password
                lead_account.wrong_password_date = None
                lead_account.save()
                messages.info(request, 'Lead Account {} password is marked as correct.'.format(lead_account))
                return None
        else:
            form = AdminLeadAccountPasswordForm(initial=dict(
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

            lead_account.wrong_password_date = timezone.now()
            lead_account.save()
            messages.info(request, 'Lead Account {} password is marked as wrong.'.format(lead_account))

    def report_correct_facebook_password(self, request, queryset):
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
                lead_account.password = new_password
                lead_account.wrong_password_date = None
                lead_account.save()
                messages.info(request, 'Lead Account {} password is marked as correct.'.format(lead_account))
                return None
        else:
            form = AdminLeadAccountPasswordForm(initial=dict(
                new_password=lead_account.password,
            ))

        return render(request, 'admin/action_with_form.html', {
            'action_name': 'report_correct_facebook_password',
            'title': 'Set new pasword for {}'.format(lead_account),
            'button': 'Save password',
            'objects': queryset,
            'form': form,
        })

    def touch(self, request, queryset):
        for lead in queryset:
            lead.touch()
            messages.info(request, 'Lead {} has been touched for {} time.'.format(lead.email, lead.touch_count))

    def sync_to_adsdb(self, request, queryset):
        for lead in queryset:
            for lead_account in lead.lead_accounts.filter(active=True):
                result = lead_account.sync_to_adsdb()
                if result:
                    messages.info(request, 'Lead Account {} is synced: {}'.format(lead_account, result))
                else:
                    messages.warning(request, 'Lead Account {} does not meet conditions to sync.'.format(lead_account))

    status_field.short_description = 'Status'
    status_field.admin_order_field = 'status'

    wrong_password_field.short_description = 'Wrong Password'
    wrong_password_field.admin_order_field = 'lead_account__wrong_password_date'

    tested_field.short_description = 'Tested'

    last_touch.admin_order_field = 'last_touch_date'
    id_field.short_description = 'ID'
    mark_as_qualified.short_description = 'Mark as Qualified, Assign RPi, create Shipstation order'
    ec2_instance_link.short_description = 'EC2 instance'

    email_field.short_description = 'Email'
    email_field.admin_order_field = 'email'

    online.boolean = True
    online.admin_order_field = 'raspberry_pi__first_seen'

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

    bundler_paid_field.short_description = 'Bundler paid'
    bundler_paid_field.boolean = True

    sync_to_adsdb.short_description = 'DEBUG: Sync to ADSDB'


class ReadOnlyLeadAdmin(LeadAdmin):
    model = ReadOnlyLead

    list_display = (
        'name',
        'status',
        'email_field',
        'phone_field',
        'bundler',
        'accounts_field',
        'links',
        'tested_field',
        'last_touch',
        'first_seen',
        'last_seen',
        'raspberry_pi',
        'ip_address',
        'usps_tracking_code',
        'online',
        'wrong_password_field',
        'pi_delivered',
        'bundler_paid_field',
    )

    actions = (
        # 'update_from_shipstation',
        'mark_as_qualified',
        'mark_as_disqualified',
        'ban_google_account',
        'unban_google_account',
        'ban_facebook_account',
        'unban_facebook_account',
        'report_wrong_google_password',
        'report_correct_google_password',
        'report_wrong_facebook_password',
        'report_correct_facebook_password',
        # 'prepare_for_testing',
        'touch',
        # 'restart_raspberry_pi',
        # 'sync_to_adsdb',
    )

    # We cannot call super().get_fields(request, obj) because that method calls
    # get_readonly_fields(request, obj), causing infinite recursion. Ditto for
    # super().get_form(request, obj). So we  assume the default ModelForm.
    def get_readonly_fields(self, request, obj=None):
        return self.fields or [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    # Allow viewing objects but not actually changing them.
    def has_change_permission(self, request, obj=None):
        return (request.method in ['GET', 'HEAD'] and
                super().has_change_permission(request, obj))

    def has_delete_permission(self, request, obj=None):
        return False

    def accounts_field(self, obj):
        result = []
        for lead_account in obj.lead_accounts.all():
            result.append(str(lead_account))

        return mark_safe(', '.join(result))

    accounts_field.short_description = 'Accounts'
