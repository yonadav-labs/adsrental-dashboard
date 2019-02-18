from django.urls import path

from adsrental.views.bookkeeper.reports_list import BookkeeperReportsListView, BookkeeperReportSendEmailsView, BookkeeperReportMarkAsPaidView
from adsrental.views.bookkeeper.report_html import BookkeeperReportHTMLView
from adsrental.views.bundler.payments import BundlerPaymentsView


urlpatterns = [
    path('reports/', BookkeeperReportsListView.as_view(), name='bookkeeper_reports_list'),
    path('reports/<int:report_id>/', BookkeeperReportHTMLView.as_view(), name='bookkeeper_report_html'),
    path('reports/<int:report_id>/send_emails', BookkeeperReportSendEmailsView.as_view(), name='bookkeeper_report_send_emails'),
    path('reports/<int:report_id>/mark_as_paid', BookkeeperReportMarkAsPaidView.as_view(), name='bookkeeper_report_mark_as_paid'),
    path('reports/preview/', BundlerPaymentsView.as_view(), name='bookkeeper_report_preview', kwargs=dict(bundler_id=None, report_id=None)),
    path('reports/view/<int:report_id>/', BundlerPaymentsView.as_view(), name='bookkeeper_report_view', kwargs=dict(bundler_id=None)),
]
