from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls import handler404, handler500  # pylint: disable=W0611
import debug_toolbar

from adsrental.views.errors import Error404View, Error500View

admin.site.site_header = 'Adsrental Administration'

urlpatterns = [
    url(r'^app/admin_tools/', include('admin_tools.urls')),
    # url(r'^admin/', admin.site.urls),
    url(r'^', include('adsrental.urls')),
    url(r'^app/admin/', admin.site.urls),
    url(r'^app/', include('adsrental.urls')),
    url(r'^app/admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^__debug__/', include(debug_toolbar.urls)),
    url(r'^robots.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /", mimetype="text/plain")),
]

handler404 = Error404View.as_view()  # noqa: F811
handler500 = Error500View.as_view()   # noqa: F811
