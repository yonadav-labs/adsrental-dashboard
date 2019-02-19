import decimal
import datetime
from dateutil import parser

from django.db.models import Count
from django.utils import timezone
from django.conf import settings

from adsrental.views.cron.base import CronView
from adsrental.models.lead_account import LeadAccount
from adsrental.models.bundler_payment import BundlerPayment


class GenerateBundlerBonusesView(CronView):
    @staticmethod
    def get_bonus(lead_accounts_count):
        for count, bonus in BundlerPayment.BONUSES:
            if lead_accounts_count >= count:
                return bonus

        return decimal.Decimal('0.00')

    def get(self, request):
        now = timezone.localtime(timezone.now())
        date_str = request.GET.get('date')
        if date_str:
            date = parser.parse(date_str).replace(tzinfo=timezone.get_current_timezone())
        else:
            date = now - datetime.timedelta(days=1)

        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + datetime.timedelta(days=1)

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
        final_bundler_stats.sort(key=lambda x: x['lead_accounts_count'], reverse=True)

        for bundler_stat in final_bundler_stats:
            bundler_stat['bonus'] = self.get_bonus(bundler_stat['lead_accounts_count'])

        bundler_payments = []
        payment_datetime = start_date
        for bundler_stat in final_bundler_stats:
            if not bundler_stat['bonus']:
                continue

            try:
                bundler_payment = BundlerPayment.objects.get(
                    bundler_id=bundler_stat['bundler_id'],
                    datetime__date=payment_datetime.date(),
                    payment_type=BundlerPayment.PAYMENT_TYPE_BONUS,
                )
            except BundlerPayment.DoesNotExist:
                bundler_payment = BundlerPayment(
                    bundler_id=bundler_stat['bundler_id'],
                    datetime=payment_datetime.date(),
                    payment_type=BundlerPayment.PAYMENT_TYPE_BONUS,
                )
            bundler_payment.payment = bundler_stat['bonus']

            extra = f"{bundler_stat['lead_accounts_count']} lead accounts"
            if bundler_stat['bonus_lead_accounts_count']:
                extra = f"{extra} ({bundler_stat['own_lead_accounts_count']} own, {bundler_stat['bonus_lead_accounts_count']} from children)"
            bundler_payment.extra = extra
            bundler_payment.ready = True
            if self.is_execute():
                bundler_payment.save()
            bundler_payments.append(bundler_payment)

        return self.render({'now': now.strftime(settings.SYSTEM_DATETIME_FORMAT), 'bundler_payments': [[i.bundler.name, str(i.payment), bundler_payment.datetime] for i in bundler_payments]})
