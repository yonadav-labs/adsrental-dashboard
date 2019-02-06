import datetime

from django.views import View
from django.utils import timezone
from django.shortcuts import render, Http404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from adsrental.models.lead_account import LeadAccount
from adsrental.models.lead import Lead
from adsrental.forms import AutoBanSoonForm


class AutoBanSoonView(View):
    template_name = 'report/autoban_soon.html'
    DAYS_BEFORE_BAN = 3

    @method_decorator(login_required)
    def get(self, request):
        if not request.user.is_superuser:
            raise Http404

        params = {
            'days': self.DAYS_BEFORE_BAN,
        }
        params.update(request.GET.dict())

        form = AutoBanSoonForm(params)

        lead_accounts = LeadAccount.objects.filter(
            active=True,
            auto_ban_enabled=True,
        )
        days_before_ban = self.DAYS_BEFORE_BAN
        ban_reasons = LeadAccount.AUTO_BAN_REASONS

        if form.is_valid():
            if form.cleaned_data['account_type']:
                lead_accounts = lead_accounts.filter(account_type=form.cleaned_data['account_type'])
            if form.cleaned_data['bundler']:
                lead_accounts = lead_accounts.filter(lead__bundler=form.cleaned_data['bundler'])
            if form.cleaned_data['days']:
                days_before_ban = form.cleaned_data['days']
            if form.cleaned_data['ban_reason']:
                ban_reasons = [form.cleaned_data['ban_reason']]

        now = timezone.localtime(timezone.now())

        wrong_password_lead_accounts = []
        if LeadAccount.BAN_REASON_AUTO_WRONG_PASSWORD in ban_reasons:
            wrong_password_lead_accounts = lead_accounts.filter(
                wrong_password_date__lte=now - datetime.timedelta(days=LeadAccount.AUTO_BAN_DAYS_WRONG_PASSWORD - days_before_ban),
                status=LeadAccount.STATUS_IN_PROGRESS,
            ).order_by('wrong_password_date').select_related('lead', 'lead__bundler')
            for lead_account in wrong_password_lead_accounts:
                lead_account.ban_timedelta = lead_account.wrong_password_date + datetime.timedelta(days=LeadAccount.AUTO_BAN_DAYS_WRONG_PASSWORD) - now

        offline_lead_accounts = []
        if LeadAccount.BAN_REASON_AUTO_OFFLINE in ban_reasons:
            offline_lead_accounts = lead_accounts.filter(
                lead__raspberry_pi__last_seen__lte=now - datetime.timedelta(days=LeadAccount.AUTO_BAN_DAYS_OFFLINE - days_before_ban),
                status=LeadAccount.STATUS_IN_PROGRESS,
            ).order_by('lead__raspberry_pi__last_seen').select_related('lead', 'lead__raspberry_pi', 'lead__bundler')
            for lead_account in offline_lead_accounts:
                lead_account.ban_timedelta = lead_account.lead.raspberry_pi.last_seen + datetime.timedelta(days=LeadAccount.AUTO_BAN_DAYS_OFFLINE) - now

        sec_checkpoint_lead_accounts = []
        if LeadAccount.BAN_REASON_AUTO_CHECKPOINT in ban_reasons:
            sec_checkpoint_lead_accounts = lead_accounts.filter(
                security_checkpoint_date__lte=now - datetime.timedelta(days=LeadAccount.AUTO_BAN_DAYS_SEC_CHECKPOINT - days_before_ban),
                status=LeadAccount.STATUS_IN_PROGRESS,
            ).order_by('security_checkpoint_date').select_related('lead', 'lead__bundler')
            for lead_account in sec_checkpoint_lead_accounts:
                lead_account.ban_timedelta = lead_account.security_checkpoint_date + datetime.timedelta(days=LeadAccount.AUTO_BAN_DAYS_SEC_CHECKPOINT) - now

        not_used_lead_accounts = []
        if LeadAccount.BAN_REASON_AUTO_NOT_USED in ban_reasons:
            not_used_lead_accounts = lead_accounts.filter(
                status=Lead.STATUS_QUALIFIED,
                lead__delivery_date__lte=now - datetime.timedelta(days=LeadAccount.AUTO_BAN_DAYS_NOT_USED - days_before_ban),
            ).order_by('lead__delivery_date').select_related('lead', 'lead__bundler')
            for lead_account in not_used_lead_accounts:
                lead_account.ban_timedelta = datetime.datetime.combine(lead_account.lead.delivery_date, datetime.datetime.min.time()).replace(tzinfo=timezone.get_default_timezone()) + datetime.timedelta(days=LeadAccount.AUTO_BAN_DAYS_NOT_USED + 1) - now

        context = dict(
            form=form,
            wrong_password_lead_accounts=wrong_password_lead_accounts,
            sec_checkpoint_lead_accounts=sec_checkpoint_lead_accounts,
            not_used_lead_accounts=not_used_lead_accounts,
            offline_lead_accounts=offline_lead_accounts,
        )

        return render(request, self.template_name, context)
