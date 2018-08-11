from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

from adsrental.models.lead_history import LeadHistory
from adsrental.models.lead_account import LeadAccount
from adsrental.admin.list_filters import DateMonthListFilter, LeadStatusListFilter


class LeadHistoryAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }

    model = LeadHistory
    list_display = (
        'id',
        'lead_link',
        'email',
        'rpid',
        'date',
        'active',
        'online',
        'amount_field',
        'wrong_password',
        'security_checkpoint',
        # 'fixes',
    )
    raw_id_fields = ('lead', )
    list_select_related = ('lead', 'lead__raspberry_pi')
    search_fields = ('lead__email', )
    list_filter = ('date', )
    actions = (
        'mark_as_online',
        'mark_as_offline',
    )

    list_filter = (DateMonthListFilter, LeadStatusListFilter, )

    def __init__(self, *args, **kwargs):
        self._request = None
        super(LeadHistoryAdmin, self).__init__(*args, **kwargs)

    def get_list_display(self, request):
        self._request = request
        list_display = super(LeadHistoryAdmin, self).get_list_display(request)
        return list_display

    def lead_link(self, obj):
        lead = obj.lead
        return mark_safe('<a target="_blank" href="{url}?q={q}">{lead}</a>'.format(
            url=reverse('admin:adsrental_lead_changelist'),
            lead=lead.name(),
            q=lead.leadid,
        ))

    def email(self, obj):
        return obj.lead.email

    def rpid(self, obj):
        return obj.lead.raspberry_pi and obj.lead.raspberry_pi.rpid

    def active(self, obj):
        return obj.is_active()

    def online(self, obj):
        return obj.is_online()

    def wrong_password(self, obj):
        return obj.is_wrong_password()

    def security_checkpoint(self, obj):
        return obj.is_sec_checkpoint()

    def amount_field(self, obj):
        amount, note = obj.get_amount_with_note()

        return mark_safe('<span class="has_note" title="{}">${}</span>'.format(
            note or 'n/a',
            amount,
        ))

    def mark_as_online(self, request, queryset):
        queryset.update(
            checks_online=24,
            checks_offline=0,
        )

    def mark_as_offline(self, request, queryset):
        queryset.update(
            checks_online=0,
            checks_offline=24,
        )

    def mark_as_correct_password_fb(self, request, queryset):
        queryset.update(
            checks_wrong_password_facebook=0,
        )

    def mark_as_correct_password_google(self, request, queryset):
        queryset.update(
            checks_wrong_password_google=0,
        )

    def mark_as_correct_password_amazon(self, request, queryset):
        queryset.update(
            checks_wrong_password_amazon=0,
        )

    def mark_as_wrong_password_fb(self, request, queryset):
        queryset.update(
            checks_wrong_password_facebook=24,
        )

    def mark_as_wrong_password_google(self, request, queryset):
        queryset.update(
            checks_wrong_password_google=24,
        )

    def mark_as_wrong_password_amazon(self, request, queryset):
        queryset.update(
            checks_wrong_password_amazon=24,
        )

    def fixes(self, obj):
        row_actions = [
            {
                'label': 'Mark as online',
                'action': 'mark_as_online',
                'enabled': not obj.is_online(),
            },
            {
                'label': 'Mark as offline',
                'action': 'mark_as_offline',
                'enabled': obj.is_online(),
            },
            {
                'label': 'Mark Facebook PW as correct',
                'action': 'mark_as_correct_password_fb',
                'enabled': obj.lead.lead_accounts.filter(account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK).count() and obj.is_wrong_password_facebook(),
            },
            {
                'label': 'Mark Google PW as correct',
                'action': 'mark_as_correct_password_google',
                'enabled': obj.lead.lead_accounts.filter(account_type=LeadAccount.ACCOUNT_TYPE_GOOGLE).count() and obj.is_wrong_password_google(),
            },
            {
                'label': 'Mark Amazon PW as correct',
                'action': 'mark_as_correct_password_amazon',
                'enabled': obj.lead.lead_accounts.filter(account_type=LeadAccount.ACCOUNT_TYPE_AMAZON).count() and obj.is_wrong_password_amazon(),
            },
            {
                'label': 'Mark Facebook PW as wrong',
                'action': 'mark_as_wrong_password_fb',
                'enabled': obj.lead.lead_accounts.filter(account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK).count() and not obj.is_wrong_password_facebook(),
            },
            {
                'label': 'Mark Google PW as wrong',
                'action': 'mark_as_wrong_password_google',
                'enabled': obj.lead.lead_accounts.filter(account_type=LeadAccount.ACCOUNT_TYPE_GOOGLE).count() and not obj.is_wrong_password_google(),
            },
            {
                'label': 'Mark Amazon PW as wrong',
                'action': 'mark_as_wrong_password_amazon',
                'enabled': obj.lead.lead_accounts.filter(account_type=LeadAccount.ACCOUNT_TYPE_AMAZON).count() and not obj.is_wrong_password_amazon(),
            },
        ]

        return mark_safe(render_to_string('django_admin_row_actions/dropdown.html', request=self._request, context=dict(
            obj=obj,
            items=row_actions,
            model_name='LeadHistoryAdmin',
        )))

    lead_link.short_description = 'Lead'

    amount_field.short_description = 'Amount'

    active.boolean = True

    online.boolean = True

    wrong_password.boolean = True

    security_checkpoint.boolean = True
