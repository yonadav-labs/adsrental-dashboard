from django.urls import path

from adsrental.views.bundler.leaderboard import BundlerLeaderboardView
from adsrental.views.bundler.payments import BundlerPaymentsView, BundlerPaymentsChargeBackView
from adsrental.views.bundler.payments_list import BundlerPaymentsListView
from adsrental.views.bundler.check import BundlerCheckView
from adsrental.views.bundler.check_days import BundlerCheckDaysView
from adsrental.views.bundler.issues_dashboard import IssuesDashboardView
from adsrental.views.bundler.issues_dashboard_actions import FixLeadAccountIssueView, RejectLeadAccountIssueView, ReportLeadAccountIssueView


urlpatterns = [  # pylint: disable=C0103
    path('<int:bundler_id>/leaderboard/', BundlerLeaderboardView.as_view(), name='bundler_leaderboard'),
    path('<int:bundler_id>/payments/', BundlerPaymentsView.as_view(), name='bundler_payments', kwargs=dict(report_id=None)),
    path('all/payments/', BundlerPaymentsView.as_view(), name='bundler_payments', kwargs=dict(bundler_id=None, report_id=None)),
    path('<int:bundler_id>/payments/<int:report_id>/', BundlerPaymentsView.as_view(), name='bundler_payments'),
    path('all/payments/<int:report_id>/', BundlerPaymentsView.as_view(), name='bundler_payments', kwargs=dict(bundler_id=None)),
    path('report/payments/<int:bundler_id>/list/', BundlerPaymentsListView.as_view(), name='bundler_report_payments_list'),
    path('report/check/<int:bundler_id>/', BundlerCheckView.as_view(), name='bundler_report_check'),
    path('report/check/<int:bundler_id>/days/<lead_id>/', BundlerCheckDaysView.as_view(), name='bundler_report_check_days'),
    path('issues/dashboard/', IssuesDashboardView.as_view(), name='bundler_issues_dashboard'),
    path('issues/dashboard/<int:lead_account_id>/', IssuesDashboardView.as_view(), name='bundler_issues_dashboard'),
    path('issues/fix/<int:lead_account_issue_id>/', FixLeadAccountIssueView.as_view(), name='bundler_fix_lead_account_issue'),
    path('issues/reject/<int:lead_account_issue_id>/', RejectLeadAccountIssueView.as_view(), name='bundler_reject_lead_account_issue'),
    path('issues/report/<int:lead_account_id>/', ReportLeadAccountIssueView.as_view(), name='bundler_report_lead_account_issue'),
    path('disable-charge-back/<int:lead_account_id>', BundlerPaymentsChargeBackView.as_view(), name='bundler_disable_charge_back_lead_account'),
]
