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

    def get_entries(self, user, year, month, search):
        lead_queryset = Lead.objects.filter(status=Lead.STATUS_QUALIFIED, raspberry_pi__isnull=False)
        if user.utm_source:
            lead_queryset = lead_queryset.filter(utm_source=user.utm_source)
        if search:
            lead_queryset = lead_queryset.filter(Lead.get_fulltext_filter(search, ['raspberry_pi__rpid', 'first_name', 'last_name', 'email', 'phone']))

        lead_id = None
        if lead_queryset.count() < 50:
            lead_id = [i.pk for i in lead_queryset]
        lead_history_queryset = LeadHistory.get_queryset_for_month(year, month, lead_id)
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
            lead.amount = 25. * lead.online_days / (lead.online_days + lead.offline_days)

        result = leads_map.values()
        result = filter(lambda x: x.online_days, result)
        result.sort(key=lambda x: x.online_days, reverse=True)
        return result

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
