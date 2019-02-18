from django.urls import path

from adsrental.views.bundler.leaderboard import BundlerLeaderboardView
from adsrental.views.bundler.payments import BundlerPaymentsView
from adsrental.views.bundler.payments_list import BundlerPaymentsListView
from adsrental.views.bundler.check import BundlerCheckView
from adsrental.views.bundler.check_days import BundlerCheckDaysView


urlpatterns = [  # pylint: disable=C0103
    path('<int:bundler_id>/leaderboard/', BundlerLeaderboardView.as_view(), name='bundler_leaderboard'),
    path('<int:bundler_id>/payments/', BundlerPaymentsView.as_view(), name='bundler_payments', kwargs=dict(report_id=None)),
    path('all/payments/', BundlerPaymentsView.as_view(), name='bundler_payments', kwargs=dict(bundler_id=None, report_id=None)),
    path('<int:bundler_id>/payments/<int:report_id>/', BundlerPaymentsView.as_view(), name='bundler_payments'),
    path('all/payments/<int:report_id>/', BundlerPaymentsView.as_view(), name='bundler_payments', kwargs=dict(bundler_id=None)),
    path('report/payments/<int:bundler_id>/list/', BundlerPaymentsListView.as_view(), name='bundler_report_payments_list'),
    path('report/check/<int:bundler_id>/', BundlerCheckView.as_view(), name='bundler_report_check'),
    path('report/check/<int:bundler_id>/days/<lead_id>/', BundlerCheckDaysView.as_view(), name='bundler_report_check_days'),
]
