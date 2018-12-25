from django.views import View
from django.shortcuts import render
from django.http import HttpResponse, HttpRequest


class RobotsView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'robots.txt', content_type='text/plain')
