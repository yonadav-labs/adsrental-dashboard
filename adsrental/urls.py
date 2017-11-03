from django.conf.urls import url
from adsrental.views.log import LogView
from adsrental.views.main import MainView

urlpatterns = [
    url(r'^$', MainView.as_view(), name='main'),
    url(r'^log.php', LogView.as_view(), name='log'),
    url(r'^log/$', LogView.as_view(), name='log'),
]
