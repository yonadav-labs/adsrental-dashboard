import html

from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from adsrental.models.lead_account_issue import LeadAccountIssue


class LeadAccountIssueAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }

    model = LeadAccountIssue
    list_display = (
        'id',
        'lead_account_field',
        'lead_field',
        'bundler_field',
        'issue_type',
        'status',
        'created',
        'buttons',
    )
    list_select_related = ('lead_account', 'lead_account__lead', 'lead_account__lead__bundler')
    list_filter = (
        'issue_type',
        'status',
        'lead_account__account_type',
    )
    search_fields = (
        'lead__account__username',
        'lead__account__lead__first_name',
        'lead__account__lead__last_name',
    )
    actions = (
        'reopen',
    )
    raw_id_fields = ('lead_account', )

    def __init__(self, *args, **kwargs):
        self._request = None
        super(LeadAccountIssueAdmin, self).__init__(*args, **kwargs)

    def get_list_display(self, request):
        self._request = request
        list_display = super(LeadAccountIssueAdmin, self).get_list_display(request)
        return list_display

    def lead_account_field(self, obj):
        lead_account = obj.lead_account
        if not lead_account:
            return None
        return mark_safe('<a href="{url}?id={id}">{type} {username}</a>{note}'.format(
            url=reverse('admin:adsrental_leadaccount_changelist'),
            type=lead_account.get_account_type_display(),
            username=lead_account.username,
            id=lead_account.id,
            note=f' <img src="/static/admin/img/icon-unknown.svg" title="{html.escape(lead_account.note)}" alt="?">' if lead_account.note else '',
        ))

    def lead_field(self, obj):
        lead = obj.lead_account.lead
        if not lead:
            return None
        return mark_safe('<a href="{url}?leadid={q}">{title}</a>{note}'.format(
            url=reverse('admin:adsrental_lead_changelist'),
            title=lead.name(),
            q=lead.leadid,
            note=f' <img src="/static/admin/img/icon-unknown.svg" title="{html.escape(lead.note)}" alt="?">' if lead.note else '',
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

    def reopen(self, request, queryset):
        for issue in queryset:
            if not issue.status == LeadAccountIssue.STATUS_CLOSED:
                continue
            issue.status = LeadAccountIssue.STATUS_OPEN
            issue.insert_note(f'Reopened by {request.user}')
            issue.save()

    def buttons(self, obj):
        result = []
        if obj.status == LeadAccountIssue.STATUS_OPEN:
            result.append('<a target="_blank" href="{url}"><button type="button">Fix</button></a>'.format(url=reverse('admin_helpers:fix_lead_account_issue', kwargs={'lead_account_issue_id': obj.id})))
        return mark_safe(', '.join(result))
