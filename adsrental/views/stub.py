from __future__ import unicode_literals

from django.views import View
from django.http import HttpResponse


class StubView(View):
    '''
    Empty response. used to hide website if no utm_source was provided.
    '''
    def get(self, request):
        return HttpResponse('')
