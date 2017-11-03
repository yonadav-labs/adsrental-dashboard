from django.views import View
from django.http import JsonResponse


class LogView(View):
    def get(self, request):
        return JsonResponse({
            'result': True,
        })
