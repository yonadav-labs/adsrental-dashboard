from django.conf import settings

def show_toolbar_callback(request):
    if settings.DEBUG:
        return True

    return False
