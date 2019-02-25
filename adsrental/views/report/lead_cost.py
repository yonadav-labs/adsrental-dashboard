import decimal

from django.views import View
from django.shortcuts import Http404, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Sum

from adsrental.models.lead import Lead
from adsrental.models.lead_history_month import LeadHistoryMonth
from adsrental.models.bundler_payment import BundlerPayment


class LeadCostView(View):
    @method_decorator(login_required)
    def get(self, request, leadid):
        if not request.user.is_superuser:
            raise Http404

        lead = get_object_or_404(Lead, leadid=leadid)
        lead_histories_month = LeadHistoryMonth.objects.filter(lead=lead)
        bundler_payments = BundlerPayment.objects.filter(lead_account__lead=lead, paid=True)

        lead_histories_month_total = lead_histories_month.aggregate(
            total=Sum('amount')
        )
        bundler_payments_total = bundler_payments.aggregate(
            total=Sum('payment')
        )

        total = decimal.Decimal(0.00)
        if lead_histories_month:
            total += lead_histories_month_total['total']
        if bundler_payments:
            total += bundler_payments_total['total']

        return render(request, 'report/lead_cost.html', dict(
            lead=lead,
            lead_histories_month=lead_histories_month,
            lead_histories_month_total=lead_histories_month_total,
            bundler_payments=bundler_payments,
            bundler_payments_total=bundler_payments_total,
            total=total,
        ))
