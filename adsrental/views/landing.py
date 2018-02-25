from __future__ import unicode_literals

import json

from django.views import View
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponseRedirect

from adsrental.forms import LandingForm


class TermsView(View):
    def get(self, request):
        return render(request, 'terms.html')


class LandingView(View):
    def redirect_https(self, request):
        protocol = u'https'
        host = u'{protocol}://{domain}'.format(
            protocol=protocol,
            domain=request.get_host().split(':')[0],
        )

        if settings.SSL_PORT:
            host = u'{host}:{port}'.format(
                host=host,
                port=settings.SSL_PORT,
            )

        url = u'{host}{path}'.format(
            host=host,
            path=request.get_full_path()
        )
        return HttpResponseRedirect(url)

    def get(self, request):
        if not request.is_secure():
            return self.redirect_https(request)
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
