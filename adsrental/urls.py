from django.conf.urls import url
from adsrental.views.log import LogView
from adsrental.views.main import MainView
from adsrental.views.thankyou import ThankyouView
from adsrental.views.sync_from_sf import SyncFromSFView
from adsrental.views.sync_to_sf import SyncToSFView
from adsrental.views.sync_to_adsdb import SyncToAdsdbView
from adsrental.views.sync_from_shipstation import SyncFromShipStationView
from adsrental.views.dashboard import DashboardView, CheckSentView
import django.contrib.auth.views as auth_views

urlpatterns = [
    url(r'^$', MainView.as_view(), name='home'),
    url(r'^sync/from_sf/$', SyncFromSFView.as_view(), name='sync_from_sf'),
    url(r'^sync/from_shipstation/$', SyncFromShipStationView.as_view(), name='sync_from_shipstation'),
    url(r'^sync/to_sf/$', SyncToSFView.as_view(), name='sync_to_sf'),
    url(r'^sync/to_adsdb/$', SyncToAdsdbView.as_view(), name='sync_to_adsdb'),
    url(r'^thankyou/$', ThankyouView.as_view(), name='thankyou'),
    url(r'^thankyou.html$', MainView.as_view(), name='main'),
    url(r'^dashboard/$', DashboardView.as_view(), name='dashboard'),
    url(r'^dashboard/check_sent/$', CheckSentView.as_view(), name='dashboard_check_sent'),
    url(r'^log.php', LogView.as_view(), name='log'),
    url(r'^log/$', LogView.as_view(), name='log'),
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
]
