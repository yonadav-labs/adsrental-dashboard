import decimal
import datetime
from dateutil import parser

from django.views import View
from django.utils import timezone
from django.shortcuts import Http404, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Count

from adsrental.models.lead_account import LeadAccount
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


class AdminBundlerBonusesView(View):
    @method_decorator(login_required)
    def get(self, request):
        if not request.user.is_superuser:
            raise Http404

        now = timezone.now().replace(tzinfo=timezone.get_current_timezone())
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

        bundler_stats = LeadAccount.objects.filter(
            account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK,
            lead__bundler__isnull=False,
            primary=True,
            qualified_date__gt=start_date,
            qualified_date__lt=end_date + datetime.timedelta(days=1),
        ).values(
            'lead__bundler_id',
            'lead__bundler__parent_bundler_id',
            'lead__bundler__parent_bundler__name',
            'lead__bundler__name',
        ).annotate(lead_accounts_count=Count('id')).order_by('-lead_accounts_count')
        # bundler_stats.sort(key=lambda x:x['lead_accounts_count'], reverse=True)

        parent_bundler_stats = {}

        for bundler_stat in bundler_stats:
            for lead_accounts_count, bonus in BONUSES:
                bundler_stat['bonus'] = decimal.Decimal('0.00')
                if bundler_stat['lead_accounts_count'] >= lead_accounts_count:
                    bundler_stat['bonus'] = bonus
                    break

        for bundler_stat in bundler_stats:
            if bundler_stat['lead__bundler__parent_bundler_id']:
                parent_bundler_id = bundler_stat['lead__bundler__parent_bundler_id']
                if parent_bundler_id not in  parent_bundler_stats:
                    parent_bundler_stats[parent_bundler_id] = {
                        'bundler_id': parent_bundler_id,
                        'bundler_name': bundler_stat['lead__bundler__parent_bundler__name'],
                        'lead_accounts_count': 0,
                        'bonus': decimal.Decimal('0.00'),
                    }

                parent_bundler_stats[parent_bundler_id]['lead_accounts_count'] += bundler_stat['lead_accounts_count']
                parent_bundler_stats[parent_bundler_id]['bonus'] += bundler_stat['bonus']

        parent_bundler_stats = list(parent_bundler_stats.values())
        parent_bundler_stats.sort(key=lambda x: x['lead_accounts_count'], reverse=True)

        return render(request, 'admin/bundler_bonuses.html', dict(
            bundler_stats=bundler_stats,
            parent_bundler_stats=parent_bundler_stats,
            start_date=start_date,
            end_date=end_date - datetime.timedelta(days=1),
            dates_list=dates_list,
        ))
