from __future__ import unicode_literals

from django.views import View
from django.http import HttpResponse


class StubView(View):
    def get(self, request):
        return HttpResponse('')
