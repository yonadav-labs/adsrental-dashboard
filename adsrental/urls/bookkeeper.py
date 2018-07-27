from django.urls import path

from adsrental.views.bookkeeper.reports_list import BookkeeperReportsListView, BookkeeperReportSendEmailsView, BookkeeperReportMarkAsPaidView
from adsrental.views.bookkeeper.report_html import BookkeeperReportHTMLView
from adsrental.views.bookkeeper.report_preview import BookkepperReportPreviewView


urlpatterns = [
    path('reports/', BookkeeperReportsListView.as_view(), name='bookkeeper_reports_list'),
    path('reports/<int:report_id>/', BookkeeperReportHTMLView.as_view(), name='bookkeeper_report_html'),
    path('reports/<int:report_id>/send_emails', BookkeeperReportSendEmailsView.as_view(), name='bookkeeper_report_send_emails'),
    path('reports/<int:report_id>/send_emails', BookkeeperReportMarkAsPaidView.as_view(), name='bookkeeper_report_mark_as_paid'),
    path('reports/preview/', BookkepperReportPreviewView.as_view(), name='bookkeeper_report_preview'),
]
