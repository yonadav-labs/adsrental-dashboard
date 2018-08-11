from django.views import View
from django.shortcuts import render


class RobotsView(View):
    def get(self, request):
        return render(request, 'robots.txt', content_type='text/plain')
