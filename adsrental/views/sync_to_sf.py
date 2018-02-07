from __future__ import unicode_literals

import datetime
from multiprocessing.pool import ThreadPool
from itertools import chain, islice

from django.views import View
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q

from adsrental.models import Lead
from salesforce_handler.models import Lead as SFLead


def chunks(iterable, size=10):
    iterator = iter(iterable)
    for first in iterator:
        yield chain([first], islice(iterator, size - 1))


class SyncToSFView(View):
    threads_count = 10
    chunk_size = 50

    def get(self, request):
        seconds_ago = int(request.GET.get('seconds_ago', '300'))
        all = request.GET.get('all')
        test = request.GET.get('test')
        if all:
            leads = Lead.objects.all().select_related('raspberry_pi')
        else:
            leads = Lead.objects.filter(
                Q(updated__gte=timezone.now() - datetime.timedelta(seconds=seconds_ago)) |
                Q(raspberry_pi__updated__gte=timezone.now() - datetime.timedelta(seconds=seconds_ago))
            ).select_related('raspberry_pi')

        if test:
            return JsonResponse({
                'all': all,
                'len': len(leads),
                'leads': [i.email for i in leads],
            })

        errors = []
        lead_emails = []
        for lead_chunk in chunks(leads, self.chunk_size):
            leads_map = {}
            for lead in lead_chunk:
                leads_map[lead.email] = lead

            sf_leads = SFLead.objects.filter(email__in=leads_map.keys()).simple_select_related('raspberry_pi')
            pool = ThreadPool(processes=self.threads_count)
            leads_queue = [(sf_lead, leads_map.get(sf_lead.email)) for sf_lead in sf_leads]
            res = pool.map(Lead.upsert_to_sf_thread, leads_queue)
            for result in res:
                if not result.get('result'):
                    errors.append(result)
            pool.close()
            lead_emails.extend(leads_map.keys())

        # for sf_lead in sf_leads:
        #     try:
        #         Lead.upsert_to_sf(sf_lead, leads_map.get(sf_lead.id))
        #     except Exception as e:
        #         errors.append([sf_lead.id, str(e)])

        return JsonResponse({
            'all': all,
            'result': True,
            'seconds_ago': seconds_ago,
            'lead_emails': lead_emails,
            'lead_count': len(lead_emails),
            'errors': errors,
        })
