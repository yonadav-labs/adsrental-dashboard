from django.urls import path

from adsrental.views.report.history_monthly import HistoryMonthlyView
from adsrental.views.report.lead_accounts_weekly import LeadAccountsWeeklyView


urlpatterns = [
    path('history_monthly/', HistoryMonthlyView.as_view(), name='history_monthly'),
    path('lead_accounts_weekly/', LeadAccountsWeeklyView.as_view(), name='lead_accounts_weekly'),
]
