import datetime

from django.views import View
from django.shortcuts import Http404, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone

from adsrental.models.lead_account import LeadAccount
from adsrental.forms import BanReasonForm
from adsrental.utils import get_week_boundaries_for_dt


class BanReasonView(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise Http404

        now = timezone.localtime(timezone.now())
        week_start, week_end = get_week_boundaries_for_dt(now)
        form = BanReasonForm(request.POST or dict(
            start_date=week_start,
            end_date=week_end - datetime.timedelta(days=1),
            bundler=None,
        ))
        lead_accounts = []
        if form.is_valid():
            lead_accounts = LeadAccount.objects.filter(
                status=LeadAccount.STATUS_BANNED,
                banned_date__gte=form.cleaned_data['start_date'],
                banned_date__lte=form.cleaned_data['end_date'],
            ).select_related('lead')
            if form.cleaned_data['bundler']:
                lead_accounts = lead_accounts.filter(lead__bundler=form.cleaned_data['bundler'])
            lead_accounts = lead_accounts[:500]

        return render(request, 'report/ban_reason.html', dict(
            lead_accounts=lead_accounts,
            form=form,
        ))
