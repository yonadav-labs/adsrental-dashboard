from __future__ import unicode_literals

import datetime
from urllib.parse import urlencode
import unicodecsv as csv

from django.contrib import admin
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.utils.safestring import mark_safe

from adsrental.models.ec2_instance import EC2Instance
from adsrental.models.lead_history_month import LeadHistoryMonth
from adsrental.admin.list_filters import HistoryStatusListFilter, DateMonthListFilter, LeadStatusListFilter


class LeadHistoryMonthAdmin(admin.ModelAdmin):
    model = LeadHistoryMonth
    admin_caching_enabled = True
    list_per_page = 5000
    list_display = (
        'id',
        'lead_link',
        # 'leadid',
        'lead_status',
        'rpid',
        'lead_address',
        'days_online',
        'days_offline',
        'days_wrong_password',
        'max_payment',
        'amount',
        'links',
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
    list_filter = (
        DateMonthListFilter,
        HistoryStatusListFilter,
        LeadStatusListFilter,
    )
    list_select_related = ('lead', 'lead__raspberry_pi')
    actions = (
        'export_as_csv',
        'restart_raspberry_pi',
        'start_ec2',
        'report_wrong_password',
        'report_correct_password',
        'prepare_for_reshipment',
        'touch',
    )

    def leadid(self, obj):
        return obj.lead and obj.lead.leadid

    def lead_status(self, obj):
        return obj.lead and obj.lead.status

    def rpid(self, obj):
        return obj.lead and obj.lead.raspberry_pi and obj.lead.raspberry_pi.rpid

    def lead_address(self, obj):
        return obj.lead and obj.lead.get_address()

    def get_queryset(self, request):
        queryset = super(LeadHistoryMonthAdmin, self).get_queryset(request)
        if 'date' not in request.GET:
            queryset = queryset.filter(date=datetime.date.today().replace(day=1))

        return queryset

    def max_payment(self, obj):
        return '${}'.format(round(obj.get_max_payment(), 2))

    def amount(self, obj):
        return '${}'.format(round(obj.get_amount(), 2))

    def lead_link(self, obj):
        lead = obj.lead
        return mark_safe('<a target="_blank" href="{url}?q={q}">{lead}</a>'.format(
            url=reverse('admin:adsrental_lead_changelist'),
            lead=lead.name(),
            q=lead.leadid,
        ))

    def links(self, obj):
        result = []
        result.append('<a target="_blank" href="{url}?{query}">Timestamps</a>'.format(
            url=reverse('admin:adsrental_leadhistory_changelist'),
            query=urlencode(dict(
                date=obj.date.strftime(settings.SYSTEM_DATE_FORMAT),
                q=obj.lead.email,
                o='-5',
            )),
        ))
        return mark_safe(', '.join(result))

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

    def start_ec2(self, request, queryset):
        for lead_history_month in queryset:
            lead = lead_history_month.lead
            EC2Instance.launch_for_lead(lead)

    def restart_raspberry_pi(self, request, queryset):
        for lead in queryset:
            if not lead.raspberry_pi:
                messages.warning(request, 'Lead {} does not haave RaspberryPi assigned, skipping'.format(lead.email))
                continue

            lead.raspberry_pi.restart_required = True
            lead.raspberry_pi.save()
            messages.info(request, 'Lead {} RPi restart successfully requested. RPi and tunnel should be online in two minutes.'.format(lead.email))

    def report_wrong_password(self, request, queryset):
        for lead_history_month in queryset:
            lead = lead_history_month.lead
            if lead.wrong_password_date is None:
                lead.wrong_password_date = timezone.now()
                lead.save()
                messages.info(request, 'Lead {} password is marked as wrong.'.format(lead.email))

    def report_correct_password(self, request, queryset):
        for lead_history_month in queryset:
            lead = lead_history_month.lead
            if lead.wrong_password_date is not None:
                lead.wrong_password_date = None
                lead.save()
                messages.info(request, 'Lead {} password is marked as correct.'.format(lead.email))

    def touch(self, request, queryset):
        for lead_history_month in queryset:
            lead = lead_history_month.lead
            lead.touch()
            messages.info(request, 'Lead {} has been touched for {} time.'.format(lead.email, lead.touch_count))

    def prepare_for_reshipment(self, request, queryset):
        for lead_history_month in queryset:
            lead = lead_history_month.lead
            if lead.raspberry_pi:
                lead.prepare_for_reshipment(request.user)
                messages.info(request, 'Lead {} is prepared. You can now flash and test it.'.format(lead.email))
            else:
                messages.warning(request, 'Lead {} has no assigned RaspberryPi. Assign a new one first.'.format(lead.email))

    lead_link.short_description = 'Lead'
