from django.shortcuts import Http404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse

from adsrental.models.bundler import Bundler
from adsrental.models.bundler_payments_report import BundlerPaymentsReport


class BundlerPaymentsHTMLView(View):
    @method_decorator(login_required)
    def get(self, request, report_id, bundler_id):
        bundler = Bundler.objects.filter(id=int(bundler_id)).first()
        if not bundler:
            raise Http404

        if not request.user.is_superuser and request.user.bundler != bundler:
            raise Http404

        report = BundlerPaymentsReport.objects.get(id=int(report_id))
        if request.user.is_superuser:
            return HttpResponse(report.get_html_for_bundler(bundler))

        if request.user.bundler == bundler:
            return HttpResponse(report.get_html_for_bundler(bundler))

        raise Http404
