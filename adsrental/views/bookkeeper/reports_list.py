import datetime

from django.conf import settings
from django.contrib import messages
from django.views import View
from django.shortcuts import render, Http404, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from adsrental.models.bundler_payments_report import BundlerPaymentsReport


class BookkeeperReportsListView(View):
    @method_decorator(login_required)
    def get(self, request):
        if not request.user.is_bookkeeper():
            raise Http404
        return render(request, 'bookkeeper/reports_list.html', context=dict(
            reports=BundlerPaymentsReport.objects.filter(cancelled=False).order_by('-date'),
            bundler=request.user.bundler,
            date__gte=datetime.date(2018, 5, 2),
        ))


class BookkeeperReportSendEmailsView(View):
    @method_decorator(login_required)
    def get(self, request, report_id):
        if not request.user.is_bookkeeper():
            raise Http404

        report = get_object_or_404(BundlerPaymentsReport, id=report_id)
        report.send_by_email()

        messages.success(request, 'Emails with report for {} were successfully sent.'.format(
            report.date.strftime(settings.HUMAN_DATE_FORMAT),
        ))
        return redirect('bookkeeper_reports_list')


class BookkeeperReportMarkAsPaidView(View):
    @method_decorator(login_required)
    def get(self, request, report_id):
        if not request.user.is_bookkeeper():
            raise Http404

        report = get_object_or_404(BundlerPaymentsReport, id=report_id)
        report.send_by_email()

        messages.success(request, 'Report for {} was successfuly marked as paid.'.format(
            report.date.strftime(settings.HUMAN_DATE_FORMAT),
        ))
        return redirect('bookkeeper_reports_list')
