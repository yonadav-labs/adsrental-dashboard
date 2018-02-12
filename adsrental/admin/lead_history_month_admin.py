from __future__ import unicode_literals

import datetime
import unicodecsv as csv

from django.contrib import admin
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponse

from adsrental.models.lead_history_month import LeadHistoryMonth
from adsrental.admin.list_filters import HistoryStatusListFilter, DateMonthListFilter


class LeadHistoryMonthAdmin(admin.ModelAdmin):
    model = LeadHistoryMonth
    list_per_page = 5000
    list_display = (
        'id',
        'lead_link',
        'rpid',
        'lead_address',
        'days_online',
        'days_offline',
        'days_wrong_password',
        'amount',
    )
    csv_fields = (
        ('leadid', 'Lead'),
        ('rpid', 'RPID', ),
        ('lead__first_name', 'First Name', ),
        ('lead__last_name', 'Last Name', ),
        ('lead__street', 'Street', ),
        ('lead__city', 'City', ),
        ('lead__state', 'State', ),
        ('lead__postal_code', 'Postal Code', ),
        ('days_online', 'Days online'),
        ('days_offline', 'Days offline'),
        ('days_wrong_password', 'Days wrong password'),
        ('amount', 'Amount'),
    )
    search_fields = ('lead__raspberry_pi__rpid', 'lead__first_name', 'lead__last_name', 'lead__email', 'lead__phone', )
    list_filter = (DateMonthListFilter, HistoryStatusListFilter, )
    list_select_related = ('lead', 'lead__raspberry_pi')
    actions = ('export_as_csv', )

    def leadid(self, obj):
        return obj.lead and obj.lead.leadid

    def rpid(self, obj):
        return obj.lead and obj.lead.raspberry_pi and obj.lead.raspberry_pi.rpid

    def lead_address(self, obj):
        return obj.lead and obj.lead.get_address()

    def get_queryset(self, request):
        queryset = super(LeadHistoryMonthAdmin, self).get_queryset(request)
        if 'date' not in request.GET:
            queryset = queryset.filter(date=datetime.date.today().replace(day=1))

        return queryset

    def amount(self, obj):
        return '${}'.format(round(obj.get_amount(), 2))

    def lead_link(self, obj):
        lead = obj.lead
        return '<a target="_blank" href="{url}?q={q}">{lead}</a>'.format(
            url=reverse('admin:adsrental_lead_changelist'),
            lead=lead.name(),
            q=lead.leadid,
        )

    def export_as_csv(self, request, queryset):
        field_names = [i[0] for i in self.csv_fields]
        field_titles = [i[1] for i in self.csv_fields]
        date = (datetime.datetime.strptime(request.GET.get('date'), settings.SYSTEM_DATE_FORMAT) if request.GET.get('date') else timezone.now()).date()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=check_report__{month}_{year}.csv'.format(
            month=date.strftime('%b').lower(),
            year=date.strftime('%Y'),
        )

        writer = csv.writer(response, encoding='utf-8')
        writer.writerow(field_titles)
        for obj in queryset:
            row = []
            for field in field_names:
                if hasattr(self, field) and callable(getattr(self, field)):
                    row.append(getattr(self, field)(obj))
                    continue
                if hasattr(obj, field) and callable(getattr(obj, field)):
                    row.append(getattr(obj, field)())
                    continue

                item = obj
                for subfield in field.split('__'):
                    item = getattr(item, subfield)
                row.append(item)
            writer.writerow(row)
        return response

    lead_link.short_description = 'Lead'
    lead_link.allow_tags = True
