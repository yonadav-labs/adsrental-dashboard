import datetime

from django.views import View
from django.shortcuts import render, get_object_or_404, Http404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from adsrental.models.bundler_payments_report import BundlerPaymentsReport
from adsrental.models.bundler import Bundler


class BundlerPaymentsListView(View):
    @method_decorator(login_required)
    def get(self, request, bundler_id):
        bundler = get_object_or_404(Bundler, id=bundler_id)
        if not request.user.can_access_bundler(bundler):
            raise Http404

        return render(request, 'bundler_payments_list.html', context=dict(
            reports=BundlerPaymentsReport.objects.filter(cancelled=False).order_by('-date'),
            bundler=bundler,
            date__gte=datetime.date(2018, 5, 2),
        ))
