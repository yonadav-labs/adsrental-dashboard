from django.urls import path

from adsrental.views.bundler.leaderboard import BundlerLeaderboardView
from adsrental.views.bundler.payments import BundlerPaymentsView
from adsrental.views.bundler.lead_payments import BundlerLeadPaymentsView
from adsrental.views.bundler.payments_html import BundlerPaymentsHTMLView
from adsrental.views.bundler.admin_payments_html import BundlerAdminPaymentsHTMLView
from adsrental.views.bundler.payments_list import BundlerPaymentsListView
from adsrental.views.bundler.check import BundlerCheckView
from adsrental.views.bundler.check_days import BundlerCheckDaysView


urlpatterns = [  # pylint: disable=C0103
    path('<int:bundler_id>/leaderboard/', BundlerLeaderboardView.as_view(), name='bundler_leaderboard'),
    path('<int:bundler_id>/lead_payments/', BundlerLeadPaymentsView.as_view(), name='bundler_lead_payments'),
    path('all/lead_payments/', BundlerLeadPaymentsView.as_view(), name='bundler_lead_payments', kwargs=dict(bundler_id='all')),
    path('<int:bundler_id>/payments/', BundlerPaymentsView.as_view(), name='bundler_payments'),
    path('all/payments/', BundlerPaymentsView.as_view(), name='bundler_payments', kwargs=dict(bundler_id='all')),
    path('report/payments/<int:report_id>/', BundlerAdminPaymentsHTMLView.as_view(), name='admin_bundler_report_payments'),
    path('report/payments/<int:report_id>/<int:bundler_id>/', BundlerPaymentsHTMLView.as_view(), name='bundler_report_payments'),
    path('report/payments/list/', BundlerPaymentsListView.as_view(), name='bundler_report_payments_list'),
    path('report/check/<int:bundler_id>/', BundlerCheckView.as_view(), name='bundler_report_check'),
    path('report/check/<int:bundler_id>/days/<lead_id>/', BundlerCheckDaysView.as_view(), name='bundler_report_check_days'),
]
