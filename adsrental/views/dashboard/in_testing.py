import datetime

from django.views import View
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from adsrental.models.raspberry_pi import RaspberryPi


class InTestingView(View):
    @method_decorator(login_required)
    def get(self, request):
        now = timezone.localtime(timezone.now())
        raspberry_pis = RaspberryPi.objects.filter(
            first_seen__isnull=True,
            first_tested__isnull=False,
            first_tested__gt=now - datetime.timedelta(days=3),
        ).select_related('lead').order_by('-first_tested')[:100]
        return render(request, 'dashboard/in_testing.html', dict(
            entries=raspberry_pis,
        ))
