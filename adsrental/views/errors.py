from django.shortcuts import render
from django.http import HttpResponse, HttpRequest


def handler404(request: HttpRequest, exception: Exception) -> HttpResponse:
    return render(request, '404.html', dict(
        user=request.user,
    ), status=404)


def handler500(request: HttpRequest) -> HttpResponse:
    return render(request, '500.html', dict(
        user=request.user,
    ), status=500)
