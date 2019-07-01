from django.conf import settings
from django.http import HttpRequest

def show_toolbar_callback(request: HttpRequest) -> bool:
    if settings.TEST:
        return False

    if settings.DEBUG:
        return True

    return False
