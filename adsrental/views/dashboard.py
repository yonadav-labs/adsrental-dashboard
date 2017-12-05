from django.views import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from adsrental.models.legacy import Lead


class DashboardView(View):
    @method_decorator(login_required)
    def get(self, request):
        entries = Lead.objects.filter(utm_source=request.user.utm_source).select_related('raspberry_pi')
        entries = Lead.objects.all().select_related('raspberry_pi')

        return render(request, 'dashboard.html', dict(
            entries=entries,
        ))
