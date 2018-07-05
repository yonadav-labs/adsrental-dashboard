from django.http import HttpResponse
from django.shortcuts import Http404
from django.views import View

from adsrental.models.bundler_payments_report import BundlerPaymentsReport


class BundlerAdminPaymentsHTMLView(View):
    def get(self, request, report_id):
        report = BundlerPaymentsReport.objects.get(id=report_id)
        if not request.user.is_superuser:
            raise Http404

        return HttpResponse(report.html)
