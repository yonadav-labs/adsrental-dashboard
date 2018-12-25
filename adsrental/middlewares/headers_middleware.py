import typing

from django.http import HttpRequest, HttpResponse


class HeadersMiddleware:
    def __init__(self, get_response: typing.Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Headers"] = "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With"

        return response
