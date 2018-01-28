from django.views import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from adsrental.models.lead_history import LeadHistory
from adsrental.models.lead import Lead
from adsrental.forms import ReportForm


class ReportView(View):
    items_per_page = 100

    def get_entries(self, user, year, month):
        lead_queryset = Lead.objects.filter()
        if user.utm_source:
            lead_queryset = lead_queryset.filter(utm_source=user.utm_source)
        lead_history_queryset = LeadHistory.get_queryset_for_month(year, month)
        leads_map = {}
        for lead in lead_queryset:
            lead.online_days = 0
            lead.offline_days = 0
            lead.wrong_password_days = 0
            lead.amount = 0
            leads_map[lead.pk] = lead
        for lead_history in lead_history_queryset:
            lead = leads_map[lead_history.lead.pk]
            if lead_history.is_wrong_password():
                lead.wrong_password_days += 1
            if lead_history.is_online():
                lead.online_days += 1
            else:
                lead.offline_days += 1

        return leads_map.values()

    @method_decorator(login_required)
    def get(self, request):
        form = ReportForm(request.GET, initial=dict(
            month=ReportForm.MONTH_CURRENT,
        ))
        entries = []
        if form.is_valid():
            year, month = [int(i) for i in form.cleaned_data['month'].split('-')]
            entries = self.get_entries(request.user, year, month)

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
