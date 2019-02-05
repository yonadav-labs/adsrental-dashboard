from django.views import View
from django.http import JsonResponse, HttpRequest

from adsrental.models.lead import Lead


class FixPrimaryView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        fixed = []
        for l in Lead.objects.all().exclude(lead_account__primary=True):
            la = l.lead_accounts.all().order_by('created').first()
            if la:
                fixed.append(str(la))
                la.primary = True
                la.save()
        return JsonResponse({'result': True, 'fixed': fixed})
