from django.views import View
from django.http import HttpResponse, HttpRequest


class StubView(View):
    '''
    Empty response. used to hide website if no utm_source was provided.
    '''
    def get(self, request: HttpRequest) -> HttpResponse:
        return HttpResponse('')
