import datetime

from django.views import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from adsrental.models.lead_history_month import LeadHistoryMonth
from adsrental.forms import ReportForm


class ReportView(View):
    items_per_page = 100

    def get_entries(self, user, year, month, search):
        date = datetime.date(year, month, 1)
        queryset = LeadHistoryMonth.objects.filter(date=date).select_related('lead')
        if user.utm_source:
            queryset = queryset.filter(lead__utm_source=user.utm_source)

        return queryset

    @method_decorator(login_required)
    def get(self, request):
        form = ReportForm(request.GET, initial=dict(
            month=ReportForm.MONTH_CURRENT,
        ))
        entries = []
        if form.is_valid():
            year, month = [int(i) for i in form.cleaned_data['month'].split('-')]
            entries = self.get_entries(request.user, year, month, form.cleaned_data['search'])

        page = request.GET.get('page', 1)
        paginator = Paginator(entries, self.items_per_page)
        try:
            entries = paginator.page(page)
        except PageNotAnInteger:
            entries = paginator.page(1)
        except EmptyPage:
            entries = paginator.page(paginator.num_pages)

        return render(request, 'report.html', dict(
            entries=entries,
            form=form,
        ))
