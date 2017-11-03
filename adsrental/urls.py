from django.conf.urls import url
from adsrental.views.log import LogView

urlpatterns = [
    url(r'^log.php', LogView.as_view(), name='log'),
]
