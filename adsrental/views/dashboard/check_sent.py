from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views import View

from adsrental.models.lead import Lead


class CheckSentView(View):
    @method_decorator(login_required)
    def post(self, request):
        lead_id = request.POST.get('leadid')
        lead = Lead.objects.get(leadid=lead_id)
        lead.pi_sent = timezone.now()
        lead.save()
        return redirect('dashboard')
