from __future__ import unicode_literals

import django.contrib.auth.views as auth_views
from django.conf.urls import url

from adsrental.views.log import LogView
from adsrental.views.main import MainView
from adsrental.views.thankyou import ThankyouView
from adsrental.views.sync_to_adsdb import SyncToAdsdbView
from adsrental.views.sync_from_shipstation import SyncFromShipStationView
from adsrental.views.sync_delivered import SyncDeliveredView
from adsrental.views.dashboard import DashboardView, CheckSentView
from adsrental.views.report import ReportView
from adsrental.views.rdp import RDPDownloadView
from adsrental.views.farming import PiConfigView
from adsrental.views.signup import SignupView
from adsrental.views.photo_id import PhotoIdView
from adsrental.views.sync_offline import SyncOfflineView
from adsrental.views.sf import SFToShipstationView, SFLaunchRaspberryPiInstance
from adsrental.views.start_reverse_tunnel import StartReverseTunnelView
from adsrental.views.cron import SyncEC2View, LeadHistoryView

urlpatterns = [
    url(r'^$', SignupView.as_view(), name='home'),
    url(r'^rdp/(?P<rpid>.*)/$', RDPDownloadView.as_view(), name='rdp'),
    url(r'^sync/from_shipstation/$', SyncFromShipStationView.as_view(), name='sync_from_shipstation'),
    url(r'^sync/delivered/$', SyncDeliveredView.as_view(), name='sync_delivered'),
    url(r'^sync/to_adsdb/$', SyncToAdsdbView.as_view(), name='sync_to_adsdb'),
    url(r'^sync/offline/$', SyncOfflineView.as_view(), name='sync_offline'),
    url(r'^thankyou/$', ThankyouView.as_view(), name='thankyou'),
    url(r'^thankyou/(?P<b64_email>.*)/$', ThankyouView.as_view(), name='thankyou_email'),
    url(r'^thankyou.html$', MainView.as_view(), name='main'),
    url(r'^report/$', ReportView.as_view(), name='report'),
    url(r'^dashboard/$', DashboardView.as_view(), name='dashboard'),
    url(r'^dashboard/check_sent/$', CheckSentView.as_view(), name='dashboard_check_sent'),
    url(r'^log.php', LogView.as_view(), name='old_log'),
    url(r'^rlog.php', LogView.as_view(), name='old_rlog'),
    url(r'^log/$', LogView.as_view(), name='log'),
    url(r'^log/rlog.php$', LogView.as_view(), name='log'),
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^farming/pi_config/(?P<rpid>.*)/$', PiConfigView.as_view(), name='farming_pi_config'),
    url(r'^signup/$', SignupView.as_view(), name='signup'),
    url(r'^photo/(?P<b64_email>.*)/$', PhotoIdView.as_view(), name='photo_id'),
    url(r'^sf/to_shipstation/$', SFToShipstationView.as_view(), name='sf_to_shipstation'),
    url(r'^sf/launch_raspberry_pi_instance/$', SFLaunchRaspberryPiInstance.as_view(), name='sf_launch_raspberry_pi_instance'),
    url(r'^start_reverse_tunnel/(?P<rpid>.*)/$', StartReverseTunnelView.as_view(), name='start_reverse_tunnel'),
    url(r'^cron/sync_ec2/$', SyncEC2View.as_view(), name='cron_sync_ec2'),
    url(r'^cron/lead_history/$', LeadHistoryView.as_view(), name='cron_lead_history'),
]
