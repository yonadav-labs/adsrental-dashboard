import os
import datetime

from django.views import View
from django.http import JsonResponse
from django.conf import settings

from adsrental.models.lead import Lead
from adsrental.models.lead_history import LeadHistory
from adsrental.models.lead_history_month import LeadHistoryMonth


class LeadHistoryView(View):
    '''
    Calculate :model:`adsrental.Lead` stats and store them in :model:`adsrental.LeadHistory` and :model:`adsrental.LeadHistoryMonth`

    Parameters:

    * rpid - if provided, process only one lead, used for debug purposes
    * now - if 'true' creates or updates :model:`adsrental.LeadHistory` objects with current lead stats. Runs on cron hourly.
    * force - forde replace :model:`adsrental.LeadHistory` on run even if they are calculated
    * date - 'YYYY-MM-DD', if provided calculates :model:`adsrental.LeadHistory` from logs. Does not check worng password and potentially incaccurate.
    * aggregate - if 'true' calculates :model:`adsrental.LeadHistoryMonth`. You can also provide *date*
    '''
    def get(self, request):
        now = request.GET.get('now')
        force = request.GET.get('force')
        date = request.GET.get('date')
        rpid = request.GET.get('rpid')
        aggregate = request.GET.get('aggregate')
        banned = request.GET.get('banned', '') == 'true'
        results = []

        if now:
            leads = Lead.objects.filter(status__in=Lead.STATUSES_ACTIVE, raspberry_pi__isnull=False).prefetch_related('raspberry_pi')
            if rpid:
                leads = leads.filter(raspberry_pi__rpid=rpid)
            for lead in leads:
                LeadHistory.upsert_for_lead(lead)
            return JsonResponse({
                'result': True,
            })
        if aggregate:
            start_date = datetime.datetime.strptime(date, settings.SYSTEM_DATE_FORMAT).date() if date else datetime.date.today()
            start_date = start_date.replace(day=1)
            leads = Lead.objects.filter(raspberry_pi__last_seen__gte=start_date).prefetch_related('raspberry_pi')
            if rpid:
                leads = leads.filter(raspberry_pi__rpid=rpid)
            else:
                LeadHistoryMonth.objects.filter(date=date).delete()

            counter = 0
            for lead in leads:
                item = LeadHistoryMonth.get_or_create(lead=lead, date=start_date)
                item.aggregate()
                if item.amount or item.id:
                    item.save()
                counter += 1
                print(lead.name(), counter, leads.count())
            return JsonResponse({
                'result': True,
                'count': leads.count(),
            })
        if date:
            leads = Lead.objects.filter(status__in=Lead.STATUSES_ACTIVE, raspberry_pi__isnull=False).select_related('raspberry_pi')
            if rpid:
                leads = leads.filter(raspberry_pi__rpid=rpid)
            date = datetime.datetime.strptime(date, settings.SYSTEM_DATE_FORMAT).date()
            if force:
                LeadHistory.objects.filter(date=date, lead__raspberry_pi__rpid=rpid).delete()
            for lead in leads:
                if not force:
                    lead_history = LeadHistory.objects.filter(lead=lead, date=date).first()
                    if lead_history:
                        continue

                log_filename = '{}.log'.format(date.strftime('%Y%m%d'))
                log_path = os.path.join(settings.RASPBERRY_PI_LOG_PATH, lead.raspberry_pi.rpid, log_filename)
                checks_online = 0
                checks_offline = 24
                checks_wrong_password = 0
                if os.path.exists(log_path):
                    file_data = open(log_path).read()
                    pings_online = file_data.count('"result": true')
                    checks_online = min(pings_online // 20, 24)
                    checks_offline = 24 - checks_online
                    if 'Wrong password' in file_data:
                        checks_wrong_password = 1
                LeadHistory(
                    lead=lead,
                    date=date,
                    checks_online=checks_online,
                    checks_offline=checks_offline,
                    checks_wrong_password=checks_wrong_password,
                ).save()
                results.append([lead.email, checks_online])

            return JsonResponse({
                'results': results,
                'result': True,
            })

        return JsonResponse({
            'results': results,
            'result': False,
        })
