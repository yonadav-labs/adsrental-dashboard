from __future__ import unicode_literals

import base64
from functools import wraps

from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.conf import settings
from django.http import HttpResponseRedirect


def view_or_basicauth(view, request, *args, **kwargs):
    # Check for valid basic auth header
    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2:
            if auth[0].lower() == "basic":
                uname, passwd = base64.b64decode(auth[1].encode()).decode().split(':')
                user = authenticate(username=uname, password=passwd)
                if user is not None and user.is_active:
                    request.user = user
                    return view(request, *args, **kwargs)

    # Either they did not provide an authorization header or
    # something in the authorization attempt failed. Send a 401
    # back to them to ask them to authenticate.
    response = HttpResponse()
    response.status_code = 401
    response['WWW-Authenticate'] = 'Basic realm="%s"' % settings.BASIC_AUTH_REALM
    return response


def basicauth_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        return view_or_basicauth(view_func, request, *args, **kwargs)
    return wrapper

def https_required(function):
    def wrap(self, request, *args, **kwargs):
        if request.is_secure():
            return function(self, request, *args, **kwargs)

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

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
