from django.urls import path

from adsrental.views.report.history_monthly import HistoryMonthlyView
from adsrental.views.report.lead_accounts_weekly import LeadAccountsWeeklyView
from adsrental.views.report.autoban_soon import AutoBanSoonView


urlpatterns = [
    path('history_monthly/', HistoryMonthlyView.as_view(), name='history_monthly'),
    path('lead_accounts_weekly/', LeadAccountsWeeklyView.as_view(), name='lead_accounts_weekly'),
    path('auto_ban/', AutoBanSoonView.as_view(), name='auto_ban', kwargs=dict(account_type='all')),
    path('auto_ban/<account_type>/', AutoBanSoonView.as_view(), name='auto_ban'),
    path('auto_ban/<account_type>/<int:bundler_id>/', AutoBanSoonView.as_view(), name='auto_ban'),
]
