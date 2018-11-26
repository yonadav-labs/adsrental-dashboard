from django.urls import include, path
from django.contrib import admin
from django.conf.urls import handler404, handler500  # pylint: disable=W0611
import debug_toolbar

from adsrental.views.errors import Error404View, Error500View

admin.site.site_header = 'Adsrental Administration'

urlpatterns = [
    path('admin/tools/', include('admin_tools.urls')),
    path('admin/', admin.site.urls),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('app/admin/', admin.site.urls),
    path('', include('adsrental.urls')),
    path('app/', include(('adsrental.urls', 'adsrental'), namespace='old_schema')),
    path('__debug__/', include(debug_toolbar.urls)),
    path('api/v1/', include('restapi.urls')),
]

handler404 = Error404View.as_view()  # noqa: F811
handler500 = Error500View.as_view()   # noqa: F811
