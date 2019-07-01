import html

from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from adsrental.models.lead_account_issue import LeadAccountIssue
from adsrental.admin.list_filters import AbstractIntIDListFilter, AbstractUIDListFilter, LeadAccountStatusListFilter, LeadAccountAccountTypeListFilter
from adsrental.admin.comment_admin import CommentInline
from adsrental.admin.base import CSVExporter


class LeadAccountIDListFilter(AbstractIntIDListFilter):
    parameter_name = 'lead_account_id'
    title = 'LeadAccount ID'


class LeadLeadidListFilter(AbstractUIDListFilter):
    parameter_name = 'lead_account__lead__leadid'
    title = 'Lead ID'


class LeadAccountIssueAdmin(admin.ModelAdmin, CSVExporter):
    csv_fields = (
        'id',
        'lead_account',
        'lead_account__lead',
        'lead_account__lead__raspberry_pi',
        'lead_account__lead__bundler',
        'issue_type',
        'status',
        'old_value',
        'new_value',
        'reporter',
        'created',
    )

    csv_titles = (
        'Id',
        'Lead Account',
        'Lead',
        'Raspberry Pi',
        'Bundler',
        'Issue Type',
        'Status',
        'Old Value',
        'New Value',
        'Reporter',
        'Created',
    )

    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }

    model = LeadAccountIssue
    list_display = (
        'id',
        'lead_account_field',
        'lead_field',
        'raspberry_pi_field',
        'bundler_field',
        'issue_type',
        'status_field',
        'old_value',
        'new_value',
        'reporter',
        'created',
        'buttons',
    )
    inlines = [ CommentInline, ]
    list_select_related = ('lead_account', 'lead_account__lead', 'lead_account__lead__bundler', 'lead_account__lead__raspberry_pi',)
    list_filter = (
        LeadAccountIDListFilter,
        LeadLeadidListFilter,
        LeadAccountStatusListFilter,
        'issue_type',
        'status',
        LeadAccountAccountTypeListFilter,
    )
    search_fields = (
        'lead_account__username',
        'lead_account__lead__first_name',
        'lead_account__lead__last_name',
        'lead_account__lead__email',
        'lead_account__lead__raspberry_pi__rpid',
    )
    actions = ('export_as_csv',)

    raw_id_fields = ('lead_account', )

    def __init__(self, *args, **kwargs):
        self._request = None
        super(LeadAccountIssueAdmin, self).__init__(*args, **kwargs)

    def get_list_display(self, request):
        self._request = request
        list_display = super(LeadAccountIssueAdmin, self).get_list_display(request)
        return list_display

    def status_field(self, obj):
        comments = '\n'.join(obj.get_comments())
        return mark_safe('{name}{note}'.format(
            name=html.escape(obj.get_status_display()),
            note=f' <img src="/static/admin/img/icon-unknown.svg" title="{html.escape(comments)}" alt="?">' if comments else '',
        ))

    def old_value(self, obj):
        return obj.get_old_value() or '-'

    def lead_account_field(self, obj):
        lead_account = obj.lead_account
        if not lead_account:
            return None
        comments = '\n'.join(lead_account.get_comments())
        return mark_safe('<a href="{url}?id={id}">{type} {username}</a>{note}'.format(
            url=reverse('admin:adsrental_leadaccount_changelist'),
            type=lead_account.get_account_type_display(),
            username=lead_account.username,
            id=lead_account.id,
            note=f' <img src="/static/admin/img/icon-unknown.svg" title="{html.escape(comments)}" alt="?">' if comments else '',
        ))

    def lead_field(self, obj):
        lead = obj.lead_account.lead
        if not lead:
            return None
        comments = '\n'.join(lead.get_comments())
        return mark_safe('<a href="{url}?leadid={q}">{title}</a>{note}'.format(
            url=reverse('admin:adsrental_lead_changelist'),
            title=lead.name(),
            q=lead.leadid,
            note=f' <img src="/static/admin/img/icon-unknown.svg" title="{html.escape(comments)}" alt="?">' if comments else '',
        ))

    def raspberry_pi_field(self, obj):
        if not obj.lead_account.lead.raspberry_pi:
            return None

        return mark_safe('<a href="{url}?rpid={rpid}">{rpid}</a>'.format(
            url=reverse('admin:adsrental_raspberrypi_changelist'),
            rpid=obj.lead_account.lead.raspberry_pi.rpid,
        ))

    def bundler_field(self, obj):
        bundler = obj.lead_account.lead.bundler
        if not bundler:
            return None

        return mark_safe('<a href="{url}?q={search}">{value}</a>'.format(
            url=reverse('admin:adsrental_bundler_changelist'),
            search=html.escape(bundler.name),
            value=bundler,
        ))

    def buttons(self, obj):
        result = []
        if obj.can_be_fixed():
            result.append('<a href="{url}"><button type="button">Fix</button></a>'.format(url=reverse('bundler_fix_lead_account_issue', kwargs={'lead_account_issue_id': obj.id})))
        if obj.can_be_resolved():
            result.append('<a href="{url}"><button type="button">Resolve / Reject</button></a>'.format(url=reverse('admin_helpers:resolve_lead_account_issue', kwargs={'lead_account_issue_id': obj.id})))
        for image in obj.images.all():
            result.append(f'<a href="{image.image.url}"><button type="button">Image</button></a>')
        return mark_safe(', '.join(result))

    status_field.short_description = 'Status'
    lead_field.short_description = 'Lead'
    lead_account_field.short_description = 'Account'
    raspberry_pi_field.short_description = 'RaspberryPi'
