import typing

from django.views import View
from django.shortcuts import render
from django.http import HttpResponse, HttpRequest


class Error404View(View):
    def get(self, request: HttpRequest, **kwargs: typing.Any) -> HttpResponse:
        return render(request, '404.html', dict(
            user=request.user,
        ), status=404)


class Error500View(View):
    def get(self, request: HttpRequest, **kwargs: typing.Any) -> HttpResponse:
        return render(request, '500.html', dict(
            user=request.user,
        ), status=500)
