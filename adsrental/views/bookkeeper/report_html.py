from django.http import HttpResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from adsrental.models.bundler_payments_report import BundlerPaymentsReport


class BookkeeperReportHTMLView(View):
    @method_decorator(login_required)
    def get(self, request, report_id):
        report = BundlerPaymentsReport.objects.get(id=report_id)
        return HttpResponse(report.html)
