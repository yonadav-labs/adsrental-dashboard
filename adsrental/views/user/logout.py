from django.views import View
from django.shortcuts import redirect


class UserLogoutView(View):
    def post(self, request):
        request.session['leadid'] = None
        return redirect('user_login')
