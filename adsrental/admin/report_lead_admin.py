from __future__ import unicode_literals

from django.contrib import admin
from django.urls import reverse
from django.shortcuts import render
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils.safestring import mark_safe

from adsrental.forms import AdminPrepareForReshipmentForm
from adsrental.models.lead import ReportProxyLead
from adsrental.models.lead_account import LeadAccount
from adsrental.admin.list_filters import StatusListFilter, RaspberryPiOnlineListFilter, TouchCountListFilter, AccountTypeListFilter, LeadAccountWrongPasswordListFilter, RaspberryPiFirstSeenListFilter, BundlerListFilter, ShipDateListFilter, QualifiedDateListFilter


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
        'pi_delivered',
        'accounts_field',
        'company',
        'email',
        # 'phone',
        'raspberry_pi_link',
        'bundler_field',
        'bundler_paid_field',
        'facebook_billed',
        'google_billed',
        'touch_count',
        'last_touch',
        'first_seen',
        'last_seen',
    )
    list_filter = (
        StatusListFilter,
        RaspberryPiOnlineListFilter,
        AccountTypeListFilter,
        LeadAccountWrongPasswordListFilter,
        TouchCountListFilter,
        'company',
        ShipDateListFilter,
        QualifiedDateListFilter,
        RaspberryPiFirstSeenListFilter,
        BundlerListFilter,
        'lead_account__bundler_paid',
        'pi_delivered',
    )
    readonly_fields = ('created', 'updated', )
    search_fields = ('leadid', 'account_name', 'first_name', 'last_name', 'raspberry_pi__rpid', 'email', )
    list_select_related = ('raspberry_pi', 'bundler', )
    actions = (
        'prepare_for_testing',
        'touch',
        'restart_raspberry_pi',
    )
    list_per_page = 500

    def get_queryset(self, request):
        queryset = super(ReportLeadAdmin, self).get_queryset(request)
        queryset = queryset.prefetch_related(
            'bundler',
            'ec2instance',
            'raspberry_pi',
            'lead_accounts',
        )
        return queryset

    def rpid(self, obj):
        return obj.raspberry_pi and obj.raspberry_pi.rpid

    def bundler_field(self, obj):
        if obj.bundler:
            return obj.bundler

        return obj.utm_source

    def first_seen(self, obj):
        return obj.raspberry_pi and obj.raspberry_pi.first_seen

    def last_seen(self, obj):
        return obj.raspberry_pi and obj.raspberry_pi.last_seen

    def last_touch(self, obj):
        return mark_safe('<span title="Touched {} times">{}</span>'.format(
            obj.touch_count,
            naturaltime(obj.last_touch_date) if obj.last_touch_date else 'Never',
        ))

    def raspberry_pi_link(self, obj):
        if not obj.raspberry_pi:
            return None

        return mark_safe('<a target="_blank" href="{url}?q={rpid}">{rpid}</a>'.format(
            url=reverse('admin:adsrental_raspberrypi_changelist'),
            rpid=obj.raspberry_pi,
        ))

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

    def restart_raspberry_pi(self, request, queryset):
        for lead in queryset:
            if not lead.raspberry_pi:
                messages.warning(request, 'Lead {} does not haave RaspberryPi assigned, skipping'.format(lead.email))
                continue

            lead.raspberry_pi.restart_required = True
            lead.raspberry_pi.save()
            lead.clear_ping_cache()
            messages.info(request, 'Lead {} RPi restart successfully requested. RPi and tunnel should be online in two minutes.'.format(lead.email))

    def touch(self, request, queryset):
        for lead in queryset:
            lead.touch()
            messages.info(request, 'Lead {} has been touched for {} time.'.format(lead.email, lead.touch_count))

    def prepare_for_testing(self, request, queryset):
        if 'do_action' in request.POST:
            form = AdminPrepareForReshipmentForm(request.POST)
            if form.is_valid():
                rpids = form.cleaned_data['rpids']
                queryset = ReportProxyLead.objects.filter(raspberry_pi__rpid__in=rpids)
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

    last_touch.admin_order_field = 'last_touch_date'
    raspberry_pi_link.admin_order_field = 'raspberry_pi__rpid'
    first_seen.admin_order_field = 'raspberry_pi__first_seen'
    last_seen.admin_order_field = 'raspberry_pi__last_seen'

    raspberry_pi_link.short_description = 'RPID'

    bundler_field.short_description = 'Bundler'
    bundler_field.admin_order_field = 'utm_source'

    accounts_field.short_description = 'Accounts'

    bundler_paid_field.short_description = 'Bundler paid'
    bundler_paid_field.boolean = True

    facebook_billed.boolean = True
    google_billed.boolean = True
