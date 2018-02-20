from django.conf.urls import include, url
from django.contrib import admin

admin.site.site_header = 'Adsrental Administration'

urlpatterns = [
    url(r'^app/admin_tools/', include('admin_tools.urls')),
    url(r'^app/admin/', admin.site.urls),
    url(r'^app/', include('adsrental.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^', include('adsrental.urls')),
]
