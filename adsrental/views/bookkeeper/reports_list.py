import datetime

from django.views import View
from django.shortcuts import render, Http404
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
