from django.urls import include, path
from django.contrib import admin
from django.conf.urls import handler404, handler500  # pylint: disable=W0611
import debug_toolbar

from adsrental.views.errors import Error404View, Error500View

admin.site.site_header = 'Adsrental Administration'

urlpatterns = [
    path('app/admin_tools/', include('admin_tools.urls')),
    path('', include('adsrental.urls')),
    path('app/admin/', admin.site.urls),
    path('app/', include('adsrental.urls')),
    path('app/admin/doc/', include('django.contrib.admindocs.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
    path('robots.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /", mimetype="text/plain")),
]

handler404 = Error404View.as_view()  # noqa: F811
handler500 = Error500View.as_view()   # noqa: F811
