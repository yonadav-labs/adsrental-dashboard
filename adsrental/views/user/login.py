from django.views import View
from django.shortcuts import render, redirect

from adsrental.forms import UserLoginForm
from adsrental.models.lead import Lead


class UserLoginView(View):
    def get(self, request):
        form = UserLoginForm()
        return render(request, 'user/login.html', dict(
            form=form,
        ))

    def post(self, request):
        form = UserLoginForm(request.POST)
        if not form.is_valid():
            return render(request, 'user/login.html', dict(
                form=form,
            ))

        lead = form.get_lead(form.cleaned_data)

        request.session['leadid'] = lead.leadid
        return redirect('user_stats')
