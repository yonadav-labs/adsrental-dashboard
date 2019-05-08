import html

from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.shortcuts import render
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db.models import Value
from django.db.models.functions import Concat
from django.template.loader import render_to_string

from adsrental.models.lead import Lead
from adsrental.utils import humanize_timedelta
from adsrental.models.lead_account import LeadAccount, ReadOnlyLeadAccount, ReportProxyLeadAccount
from adsrental.models.lead_account_issue import LeadAccountIssue
from adsrental.forms import AdminLeadAccountBanForm
from adsrental.admin.list_filters import TouchCountListFilter, AccountTypeListFilter, \
    WrongPasswordListFilter, AbstractFulltextFilter, AbstractIntIDListFilter, \
    AbstractDateListFilter, StatusListFilter, BannedDateListFilter, LeadRaspberryPiOnlineListFilter, \
    LeadBundlerListFilter, SecurityCheckpointListFilter, AutoBanListFilter, LastTouchDateListFilter, \
    LeadDeliveryDateListFilter, DeliveredLastTwoDaysListFilter, titled_filter


class QualifiedDateListFilter(AbstractDateListFilter):
    title = 'Qualified date'
    field_name = 'qualified_date'
    parameter_name = 'qualified_date'


class DisqualifiedDateListFilter(AbstractDateListFilter):
    title = 'Disqualified date'
    field_name = 'disqualified_date'
    parameter_name = 'disqualified_date'


class InProgressDateListFilter(AbstractDateListFilter):
    title = 'In-Progress date'
    parameter_name = 'in_progress_date'
    field_name = 'in_progress_date'


class AddressListFilter(AbstractFulltextFilter):
    title = 'Address'
    parameter_name = 'address'
    field_names = ['lead__city', 'lead__country', 'lead__state', 'lead__postal_code', 'lead__street']


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
        'bundler_paid',
        'last_touch',
        'first_seen',
        'last_seen',
        'online',
        'touch_count_field',
        'touch_button',
        'wrong_password_date_field',
        'security_checkpoint_date_field',
        # 'primary',
        # 'billed',
        'links',
        'created',
    )
    list_select_related = ('lead', 'lead__ec2instance')
    list_filter = (
        AbstractIntIDListFilter,
        AddressListFilter,
        TouchCountListFilter,
        LastTouchDateListFilter,
        AccountTypeListFilter,
        LeadRaspberryPiOnlineListFilter,
        'bundler_paid',
        StatusListFilter,
        WrongPasswordListFilter,
        SecurityCheckpointListFilter,
        QualifiedDateListFilter,
        DisqualifiedDateListFilter,
        InProgressDateListFilter,
        BannedDateListFilter,
        LeadDeliveryDateListFilter,
        AutoBanListFilter,
        'charge_back',
        'primary',
        'ban_reason',
        'lead__company',
        ('lead__bundler__is_active', titled_filter('Lead Bundler active')),
        LeadBundlerListFilter,
        DeliveredLastTwoDaysListFilter,
    )
    search_fields = (
        'lead__leadid',
        'lead__account_name',
        'lead__first_name',
        'lead__last_name',
        'lead__phone',
        'lead__raspberry_pi__rpid',
        'lead__email',
        'username',
    )
    actions = (
        'approve_account',
        'mark_as_qualified',
        'mark_as_disqualified',
        'mark_as_available_from_disqualified',
        'ban',
        'unban',
        'report_wrong_password',
        'report_security_checkpoint',
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
        'charge_back',
        'active',
    )
    raw_id_fields = ('lead', )

    def __init__(self, *args, **kwargs):
        self._request = None
        super(LeadAccountAdmin, self).__init__(*args, **kwargs)

    def get_list_display(self, request):
        self._request = request
        list_display = super(LeadAccountAdmin, self).get_list_display(request)
        return list_display

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
        return mark_safe('{name}{note}'.format(
            name=html.escape(obj.lead.name()),
            note=f' <img src="/static/admin/img/icon-unknown.svg" title="{html.escape(obj.note)}" alt="?">' if obj.note else '',
        ))

    def lead_link(self, obj):
        lead = obj.lead
        return mark_safe('<a target="_blank" href="{url}?leadid={leadid}">{lead}</a>'.format(
            url=reverse('admin:adsrental_lead_changelist'),
            lead=lead.name(),
            leadid=obj.lead.leadid,
        ))

    def raspberry_pi_field(self, obj):
        if not obj.lead.raspberry_pi:
            return None

        return mark_safe('<a target="_blank" href="{url}?rpid={rpid}">{rpid}</a>'.format(
            url=reverse('admin:adsrental_raspberrypi_changelist'),
            rpid=obj.lead.raspberry_pi.rpid,
        ))

    def status_field(self, obj):
        title = 'Show changes'
        status = obj.status
        if obj.status == LeadAccount.STATUS_BANNED:
            dt = f'after {humanize_timedelta(obj.banned_date - obj.created, short=True)}' if obj.banned_date else ''
            status = f'{obj.status} ({obj.get_ban_reason_display()}) {dt}'
            title = obj.note if obj.note else f'Banned for {obj.get_ban_reason_display()}'
        return mark_safe('<a target="_blank" href="{url}?lead_account_id={q}" title="{title}">{status}</a>'.format(
            url=reverse('admin:adsrental_leadchange_changelist'),
            q=obj.id,
            title=title,
            status=status,
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

    def touch_button(self, obj):
        row_actions = [
            {
                'label': 'Touch',
                'action': 'touch',
                'enabled': obj.account_type in obj.ACCOUNT_TYPES_FACEBOOK,
            },
        ]
        return mark_safe(render_to_string('django_admin_row_actions/dropdown.html', request=self._request, context=dict(
            obj=obj,
            items=row_actions,
            model_name='LeadAccountAdmin',
        )))

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

    def bundler_field(self, obj):
        bundler = obj.lead.bundler
        if bundler:
            return mark_safe('<a target="_blank" href="{url}?q={q}" title="{title}">{text}</a>'.format(
                url=reverse('admin:adsrental_bundler_changelist'),
                q=bundler.email,
                title=bundler.utm_source,
                text=bundler,
            ))

        return None

    def links(self, obj):
        result = []
        result.append('<a target="_blank" href="{url}?lead_account_id={id}">Issues</a>'.format(
            url=reverse('admin:adsrental_leadaccountissue_changelist'),
            id=obj.id,
        ))
        result.append('<a target="_blank" href="{url}">Report new issue</a>'.format(
            url=reverse('admin_helpers:report_lead_account_issue', kwargs=dict(lead_account_id=obj.id)),
        ))
        result.append('<a target="_blank" href="{url}?lead_account_id={id}">Bundler payments</a>'.format(
            url=reverse('admin:adsrental_bundlerpayment_changelist'),
            id=obj.id,
        ))
        return mark_safe(', '.join(result))

    def approve_account(self, request, queryset):
        for lead_account in queryset:
            if lead_account.status != LeadAccount.STATUS_NEEDS_APPROVAL:
                messages.info(request, f'Lead Account {lead_account} should be in Neeads Approval status.')
                continue
            lead_account.set_status(LeadAccount.STATUS_IN_PROGRESS, request.user)
            lead_account.save()
            if lead_account.lead.status == Lead.STATUS_NEEDS_APPROVAL:
                lead_account.lead.set_status(LeadAccount.STATUS_IN_PROGRESS, request.user)
                lead_account.lead.save()
            messages.info(request, f'Lead Account {lead_account} approved and moved to In-Progress.')

    def mark_as_qualified(self, request, queryset):
        for lead_account in queryset:
            if lead_account.is_banned():
                messages.warning(request, '{} is {}, skipping'.format(lead_account, lead_account.status))
                continue

            lead_account.qualify(request.user)
            if lead_account.lead.assign_raspberry_pi():
                messages.success(
                    request, '{} has new Raspberry Pi assigned: {}'.format(lead_account, lead_account.lead.raspberry_pi.rpid))

            self._create_shipstation_order(request, lead_account)

    def _create_shipstation_order(self, request, lead_account):
        try:
            create_order_result = lead_account.lead.add_shipstation_order()
        except ValueError as e:
            messages.error(request, '{} order was not created: {}'.format(lead_account, e))
            return

        if create_order_result:
            messages.success(request, '{} order created: {}'.format(lead_account, lead_account.lead.shipstation_order_number))
        else:
            messages.info(request, '{} order already exists: {}.'.format(lead_account, lead_account.lead.shipstation_order_number))

    def mark_as_disqualified(self, request, queryset):
        for lead_account in queryset:
            if lead_account.status != LeadAccount.STATUS_AVAILABLE:
                messages.warning(request, '{} is {}, skipping'.format(lead_account, lead_account.status))
                continue

            lead_account.disqualify(request.user)
            messages.info(request, '{} is disqualified.'.format(lead_account))

    def mark_as_available_from_disqualified(self, request, queryset):
        for lead_account in queryset:
            if lead_account.status != LeadAccount.STATUS_DISQUALIFIED:
                messages.warning(request, f'{lead_account} is {lead_account.status}, skipping')
                continue

            lead_account.set_status(LeadAccount.STATUS_AVAILABLE, request.user)
            messages.info(request, f'{lead_account} is moved back to {lead_account.status}')

    def ban(self, request, queryset):
        if 'do_action' in request.POST:
            form = AdminLeadAccountBanForm(request.POST, request=request)
            if form.is_valid():
                reason = form.cleaned_data['reason']
                note = form.cleaned_data['note']
                for lead_account in queryset:
                    lead_account.ban(edited_by=request.user, reason=reason, note=note)
                    messages.info(request, '{} is banned.'.format(lead_account))
                return None
        else:
            form = AdminLeadAccountBanForm(request=request)

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
            if lead_account.is_wrong_password():
                messages.info(request, f'Lead Account {lead_account} was already marked as wrong, skipping.')
                continue
            lead_account.mark_wrong_password(edited_by=request.user)
            issue = LeadAccountIssue(
                lead_account=lead_account,
                issue_type=LeadAccountIssue.ISSUE_TYPE_WRONG_PASSWORD,
                reporter=request.user,
            )
            issue.insert_note(f'Reported by {request.user}')
            issue.save()
            messages.info(request, f'{lead_account} password is marked as wrong.')

    def report_security_checkpoint(self, request, queryset):
        for lead_account in queryset:
            if lead_account.is_security_checkpoint_reported():
                messages.info(request, '{} security checkpoint is already reported, skipping.'.format(lead_account))
                continue

            lead_account.mark_security_checkpoint(edited_by=request.user)
            issue = LeadAccountIssue(
                lead_account=lead_account,
                issue_type=LeadAccountIssue.ISSUE_TYPE_SECURITY_CHECKPOINT,
                reporter=request.user,
            )
            issue.insert_note(f'Reported by {request.user}')
            issue.save()
            messages.info(request, '{} security checkpoint reported.'.format(lead_account))

    def sync_to_adsdb(self, request, queryset):
        for lead_account in queryset:
            lead = lead_account.get_lead()

            if not lead.is_active():
                messages.warning(request, '{} is now {}, skipping.'.format(lead.email, lead.status))
                continue

            if lead.touch_count < lead.ADSDB_SYNC_MIN_TOUCH_COUNT:
                lead.touch_count = lead.ADSDB_SYNC_MIN_TOUCH_COUNT
                lead.last_touch_date = timezone.now()
                lead.save()
                messages.warning(request, '{} touch count has been increased to meet conditions.'.format(lead.email))

            result = lead_account.sync_to_adsdb()
            if result:
                messages.info(request, '{} is synced: {}'.format(lead_account, result))
            else:
                messages.warning(request, '{} does not meet conditions to sync.'.format(lead_account))

    @staticmethod
    def touch(instance, request, queryset):
        for lead_account in queryset:
            lead_account.touch()
            messages.info(request, '{} has been touched for {} time.'.format(lead_account, lead_account.touch_count))

    lead_link.short_description = 'Lead'
    lead_link.admin_order_field = Concat('lead__first_name', Value(' '), 'lead__last_name')

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


class ReportLeadAccountAdmin(LeadAccountAdmin):
    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }

    model = ReportProxyLeadAccount
    # admin_caching_enabled = True
    list_per_page = 500
    list_display = (
        'id',
        'name',
        'lead_link',
        'raspberry_pi_field',
        'account_type',
        'status_field',
        'username',
        'password',
        'bundler_field',
        'bundler_paid',
        'first_seen',
        'last_seen',
        'online',
        'last_touch',
        'adsdb_account_id',
        'wrong_password_date_field',
        'security_checkpoint_date_field',
        'sync_with_adsdb',
        'billed',
    )


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
        'report_security_checkpoint',
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
        return mark_safe('<a target="_blank" href="{url}?leadid={leadid}">{lead}</a>'.format(
            url=reverse('admin:adsrental_readonlylead_changelist'),
            lead=lead.name(),
            leadid=lead.leadid,
        ))

    def raspberry_pi_field(self, obj):
        if not obj.lead.raspberry_pi:
            return None

        return obj.lead.raspberry_pi

    lead_link.short_description = 'Lead'
    lead_link.admin_order_field = Concat('lead__first_name', Value(' '), 'lead__last_name')

    raspberry_pi_field.short_description = 'Raspberry Pi'
