from django.urls import include, path
from rest_framework.schemas import get_schema_view

from restapi.routers import main_router
from restapi.views import login_view

schema_view = get_schema_view(title='Adsrental API')

urlpatterns = [
    path('schema/', schema_view),
    path('', include(main_router.urls)),
    path('auth/', include('rest_framework.urls')),
    path('login/', login_view),
]
