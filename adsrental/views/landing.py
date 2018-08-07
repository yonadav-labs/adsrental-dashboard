from __future__ import unicode_literals

import json

from django.views import View
from django.shortcuts import render, redirect

from adsrental.forms import LandingForm
from adsrental.models.bundler import Bundler
from adsrental.decorators import https_required


class TermsView(View):
    def get(self, request):
        return render(request, 'terms.html')


class LandingView(View):
    @https_required
    def get(self, request):
        if 'utm_source' in request.GET:
            utm_source = request.GET.get('utm_source')
            request.session['utm_source'] = utm_source

        utm_source = request.session.get('utm_source')
        bundler = Bundler.objects.filter(utm_source=utm_source, is_active=True).first()
        if not utm_source or not bundler:
            if request.user.is_authenticated:
                return redirect('main')
            return redirect('user_login')

        return render(request, 'landing.html', dict(
            user=request.user,
            form=LandingForm(),
        ))

    @https_required
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
