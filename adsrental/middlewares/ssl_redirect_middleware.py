import typing

from django.conf import settings
from django.http import HttpResponsePermanentRedirect, HttpRequest, HttpResponse
from django.views import View


SSL_ON = getattr(settings, 'SSL_ON', True)
SSL_ALWAYS = getattr(settings, 'SSL_ALWAYS', False)
HTTPS_PATHS = getattr(settings, 'HTTPS_PATHS', [])
SSL_PORT = getattr(settings, 'SSL_PORT', None)
SSL_KW = 'SSL'


class SSLRedirectMiddleware:
    def process_view(self, request: HttpRequest, view_func: View, view_args: typing.List[str], view_kwargs: typing.Dict[str, str]) -> HttpResponse:
        response_is_secure = self._response_is_secure(
            request, view_func, view_args, view_kwargs)
        if response_is_secure != self._request_is_secure(request):
            return self._redirect(request, response_is_secure)

    def _response_is_secure(self, request: HttpRequest, view_func: View, view_args: typing.List[str], view_kwargs: typing.Dict[str, str]) -> bool:
        if not SSL_ON:
            return False

        if SSL_ALWAYS:
            return True

        if SSL_KW in view_kwargs:
            return bool(view_kwargs[SSL_KW])

        for path in HTTPS_PATHS:
            if request.path.startswith(f'/{path}'):
                return True

        return False

    def _request_is_secure(self, request: HttpRequest) -> bool:
        if request.is_secure():
            return True

        if 'HTTP_X_FORWARDED_SSL' in request.META:
            return request.META['HTTP_X_FORWARDED_SSL'] == 'on'

        if ('HTTP_X_FORWARDED_HOST' in request.META
                and request.META['HTTP_X_FORWARDED_HOST'].endswith('443')):
            return True

        return False

    def _redirect(self, request: HttpRequest, secure: bool) -> HttpResponse:
        protocol = u'https' if secure else u'http'
        host = u'{protocol}://{domain}'.format(
            protocol=protocol,
            domain=request.get_host().split(':')[0],
        )

        if not secure:
            host = host.replace(':443', '')
        if secure and SSL_PORT:
            host = u'{host}:{port}'.format(
                host=host,
                port=SSL_PORT,
            )

        url = u'{host}{path}'.format(
            host=host,
            path=request.get_full_path()
        )
        return HttpResponsePermanentRedirect(url)
