from django.conf.urls import include, url
from django.contrib import admin

admin.site.site_header = 'Adsrental Administration'

urlpatterns = [
    url(r'^app/admin/', admin.site.urls),
    url(r'^app/', include('adsrental.urls')),
]
