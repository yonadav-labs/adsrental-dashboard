from django.urls import path

from adsrental.views.bookkeeper.reports_list import BookkeeperReportsListView
from adsrental.views.bookkeeper.report_html import BookkeeperReportHTMLView


urlpatterns = [
    path('reports/', BookkeeperReportsListView.as_view(), name='bookkeeper_reports_list'),
    path('reports/<int:report_id>/', BookkeeperReportHTMLView.as_view(), name='bookkeeper_report_html'),
]
