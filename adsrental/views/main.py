from django.views import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse, HttpRequest


class MainView(View):
    @method_decorator(login_required)
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'main.html', dict(
            user=request.user,
            bundler=request.user.bundler,
        ))
