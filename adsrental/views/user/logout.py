from django.views import View
from django.shortcuts import redirect
from django.http import HttpResponse, HttpRequest


class UserLogoutView(View):
    def post(self, request: HttpRequest) -> HttpResponse:
        request.session['leadid'] = None
        return redirect('user_login')
