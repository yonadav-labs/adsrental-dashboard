import decimal
import datetime

from django.db.models import Count
from django.utils import timezone

from adsrental.views.cron.base import CronView
from adsrental.models.lead_account import LeadAccount
from adsrental.models.bundler_payment import BundlerPayment
from adsrental.utils import get_week_boundaries_for_dt


class GenerateBundlerBonusesView(CronView):
    @staticmethod
    def get_bonus(lead_accounts_count):
        for count, bonus in BundlerPayment.BONUSES:
            if lead_accounts_count >= count:
                return bonus

        return decimal.Decimal('0.00')

    def get(self, request):
        now = timezone.now()
        date = now - datetime.timedelta(days=1)

        start_date, end_date = get_week_boundaries_for_dt(date)

        bundler_stats = LeadAccount.objects.filter(
            account_type__in=LeadAccount.ACCOUNT_TYPES_FACEBOOK,
            lead__bundler__isnull=False,
            primary=True,
            qualified_date__gt=start_date,
            qualified_date__lt=end_date,
        ).values(
            'lead__bundler_id',
            'lead__bundler__bonus_receiver_bundler_id',
            'lead__bundler__bonus_receiver_bundler__name',
            'lead__bundler__name',
        ).annotate(lead_accounts_count=Count('id')).order_by('-lead_accounts_count')

        final_bundler_stats = {}

        for bundler_stat in bundler_stats:
            bundler_id = bundler_stat['lead__bundler_id']
            bundler_name = bundler_stat['lead__bundler__name']
            bonus_lead_accounts = False
            if bundler_stat['lead__bundler__bonus_receiver_bundler_id']:
                bundler_id = bundler_stat['lead__bundler__bonus_receiver_bundler_id']
                bundler_name = bundler_stat['lead__bundler__bonus_receiver_bundler__name']
                bonus_lead_accounts = True

            if bundler_id not in final_bundler_stats:
                final_bundler_stats[bundler_id] = {
                    'bundler_id': bundler_id,
                    'bundler_name': bundler_name,
                    'lead_accounts_count': 0,
                    'bonus_lead_accounts_count': 0,
                    'own_lead_accounts_count': 0,
                    'bonus': decimal.Decimal('0.00'),
                }

            final_bundler_stats[bundler_id]['lead_accounts_count'] += bundler_stat['lead_accounts_count']
            if bonus_lead_accounts:
                final_bundler_stats[bundler_id]['bonus_lead_accounts_count'] += bundler_stat['lead_accounts_count']
            else:
                final_bundler_stats[bundler_id]['own_lead_accounts_count'] += bundler_stat['lead_accounts_count']

        final_bundler_stats = list(final_bundler_stats.values())

        for bundler_stat in final_bundler_stats:
            bundler_stat['bonus'] = self.get_bonus(bundler_stat['lead_accounts_count'])

        bundler_payments = []
        for bundler_stat in final_bundler_stats:
            if not bundler_stat['bonus']:
                continue

            payment_datetime = start_date
            bundler_payment, _ = BundlerPayment.objects.get_or_create(
                bundler_id=bundler_stat['bundler_id'],
                datetime__date=payment_datetime.date(),
                payment_type=BundlerPayment.PAYMENT_TYPE_BONUS,
                defaults=dict(payment=bundler_stat['bonus']),
            )
            bundler_payment.payment = bundler_stat['bonus']
            bundler_payment.datetime = payment_datetime
            bundler_payment.ready = end_date < now
            if self.is_execute():
                bundler_payment.save()
            bundler_payments.append(bundler_payment)

        return self.render({'bundler_payments': [[i.bundler.name, str(i.payment), i.ready] for i in bundler_payments]})
