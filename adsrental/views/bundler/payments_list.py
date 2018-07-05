import datetime

from django.views import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from adsrental.models.bundler_payments_report import BundlerPaymentsReport


class BundlerPaymentsListView(View):
    @method_decorator(login_required)
    def get(self, request):
        return render(request, 'bundler_payments_list.html', context=dict(
            reports=BundlerPaymentsReport.objects.filter(cancelled=False).order_by('-date'),
            bundler=request.user.bundler,
            date__gte=datetime.date(2018, 5, 2),
        ))
