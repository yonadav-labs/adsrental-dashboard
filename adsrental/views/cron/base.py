from dateutil import parser

from django.utils import timezone
from django.views import View
from django.conf import settings
from django.http import JsonResponse


class CronView(View):
    _request = None

    def _cron_check(self, request):
        if request.user.is_authenticated and request.user.is_superuser:
            return True
        if request.META.get('HTTP_SECRET', '') == settings.CRON_SECRET:
            return True

        return False

    def render(self, data):
        return JsonResponse(data)

    def dispatch(self, request, *args, **kwargs):
        if not self._cron_check(request):
            return JsonResponse({'error': 'Access denied'})

        self._request = request
        return super(CronView, self).dispatch(request, *args, **kwargs)

    def is_execute(self):
        return True if self._request.GET.get('execute', '') == 'true' else False

    def get_datetime(self):
        date_str = self._request.GET.get('date')
        if date_str:
            return parser.parse(date_str).replace(tzinfo=timezone.get_current_timezone())
        else:
            return timezone.localtime(timezone.now())
