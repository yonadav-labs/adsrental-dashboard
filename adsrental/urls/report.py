from django.urls import path

from adsrental.views.report.history_monthly import HistoryMonthlyView
from adsrental.views.report.lead_accounts_weekly import LeadAccountsWeeklyView
from adsrental.views.report.autoban_soon import AutoBanSoonView
from adsrental.views.report.bundler_payments import BundlerPaymentsView
from adsrental.views.report.lead_cost import LeadCostView


urlpatterns = [
    path('history_monthly/', HistoryMonthlyView.as_view(), name='history_monthly'),
    path('lead_accounts_weekly/', LeadAccountsWeeklyView.as_view(), name='lead_accounts_weekly'),
    path('auto_ban/', AutoBanSoonView.as_view(), name='auto_ban'),
    path('bundler_payments/', BundlerPaymentsView.as_view(), name='bundler_payments'),
    path('lead_cost/<leadid>/', LeadCostView.as_view(), name='lead_cost'),
]
