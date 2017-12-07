from django.conf.urls import url
from adsrental.views.log import LogView
from adsrental.views.main import MainView
from adsrental.views.thankyou import ThankyouView
from adsrental.views.sync_from_sf import SyncFromSFView
from adsrental.views.dashboard import DashboardView
import django.contrib.auth.views as auth_views

urlpatterns = [
    url(r'^$', MainView.as_view(), name='home'),
    url(r'^sync/from_sf/$', SyncFromSFView.as_view(), name='sync_from_sf'),
    url(r'^thankyou/$', ThankyouView.as_view(), name='thankyou'),
    url(r'^thankyou.html$', MainView.as_view(), name='main'),
    url(r'^dashboard/$', DashboardView.as_view(), name='dashboard'),
    url(r'^log.php', LogView.as_view(), name='log'),
    url(r'^log/$', LogView.as_view(), name='log'),
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
]
