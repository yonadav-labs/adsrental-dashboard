from __future__ import unicode_literals

from django.views import View
from django.shortcuts import render


class Error404View(View):
    def get(self, request):
        return render(request, '404.html', dict(
            user=request.user,
        ))


class Error500View(View):
    def get(self, request):
        return render(request, '500.html', dict(
            user=request.user,
        ))
