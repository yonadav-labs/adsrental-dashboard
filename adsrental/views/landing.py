from __future__ import unicode_literals

import json

from django.views import View
from django.http import HttpResponse
from django.shortcuts import render, redirect

from adsrental.forms import LandingForm


class LandingView(View):
    def get(self, request):
        if 'utm_source' in request.GET:
            utm_source = request.GET.get('utm_source')
            request.session['utm_source'] = utm_source

        utm_source = request.session.get('utm_source')
        if not utm_source:
            return HttpResponse('')

        return render(request, 'landing.html', dict(
            user=request.user,
            form=LandingForm(),
        ))

    def post(self, request):
        form = LandingForm(request.POST)
        if form.is_valid():
            request.session['landing_form_data'] = json.dumps({
                'email': form.cleaned_data['email'],
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
            })
            return redirect('signup')

        return render(request, 'landing.html', dict(
            user=request.user,
            form=form,
        ))
