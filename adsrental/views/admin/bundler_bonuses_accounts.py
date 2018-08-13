import decimal
import datetime
from dateutil import parser

from django.views import View
from django.utils import timezone
from django.shortcuts import Http404, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from adsrental.models.lead_account import LeadAccount
from adsrental.models.bundler import Bundler
from adsrental.utils import get_week_boundaries_for_dt

BONUSES = [
    [100, decimal.Decimal(3000)],
    [90, decimal.Decimal(2500)],
    [80, decimal.Decimal(2000)],
    [70, decimal.Decimal(1500)],
    [60, decimal.Decimal(1000)],
    [50, decimal.Decimal(500)],
    [40, decimal.Decimal(400)],
    [30, decimal.Decimal(300)],
    [20, decimal.Decimal(200)],
    [10, decimal.Decimal(100)],
]


class AdminBundlerBonusesAccountsView(View):
    @method_decorator(login_required)
    def get(self, request, bundler_id):
        if not request.user.is_superuser:
            raise Http404

        bundler = Bundler.objects.filter(id=bundler_id).first()
        if not bundler:
            raise Http404

        now = timezone.now()
        date = request.GET.get('date')
        if date:
            date = parser.parse(date).replace(tzinfo=timezone.get_current_timezone())
        else:
            date = now

        start_date, end_date = get_week_boundaries_for_dt(date)

        dates_list = []
        for i in range(-1, 2):
            if start_date + datetime.timedelta(days=7 * i) < now:
                dates_list.append(dict(
                    start_date=start_date + datetime.timedelta(days=7 * i),
                    end_date=end_date + datetime.timedelta(days=7 * i) - datetime.timedelta(days=1),
                ))

        lead_accounts = LeadAccount.objects.filter(
            account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK,
            lead__bundler=bundler,
            primary=True,
            qualified_date__gt=start_date,
            qualified_date__lt=end_date + datetime.timedelta(days=1),
        ).prefetch_related('lead').order_by('qualified_date')

        return render(request, 'admin/bundler_bonuses_accounts.html', dict(
            lead_accounts=lead_accounts,
            bundler=bundler,
            start_date=start_date,
            end_date=end_date - datetime.timedelta(days=1),
            dates_list=dates_list,
        ))
