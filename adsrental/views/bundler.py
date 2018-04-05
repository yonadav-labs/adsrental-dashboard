from django.shortcuts import render, Http404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models.functions import TruncDay
from django.db.models import Count

from adsrental.models.lead_account import LeadAccount


class BundlerReportView(View):
    @method_decorator(login_required)
    def get(self, request):
        bundler = request.user.bundler
        if not bundler:
            raise Http404

        lead_accounts_by_qualified_date = (
            LeadAccount.objects
            .filter(lead__bundler=bundler, qualified_date__isnull=False)
            .annotate(date=TruncDay('qualified_date'))
            .values('date') 
            .annotate(count=Count('id')) 
            .values('date', 'count') 
        )

        return render(request, 'bundler_dashboard.html', dict(
            user=request.user,
            bundler=bundler,
            entries=lead_accounts_by_qualified_date,
        ))
