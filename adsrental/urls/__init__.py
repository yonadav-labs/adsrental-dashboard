import django.contrib.auth.views as auth_views
from django.conf.urls import url
from django.urls import include, path

from adsrental.views.log import LogView, ShowLogDirView, ShowLogView
from adsrental.views.main import MainView
from adsrental.views.stub import StubView
from adsrental.views.thankyou import ThankyouView
from adsrental.views.dashboard import DashboardView, CheckSentView, SetPasswordView
from adsrental.views.report import ReportView
from adsrental.views.rdp import RDPDownloadView, RDPConnectView
from adsrental.views.farming import PiConfigView
from adsrental.views.signup import SignupView
from adsrental.views.photo_id import PhotoIdView
from adsrental.views.sf import SFToShipstationView, SFLaunchRaspberryPiInstance
from adsrental.views.ec2_ssh import StartReverseTunnelView, GetNetstatView
from adsrental.views.rpi import EC2DataView
from adsrental.views.landing import LandingView, TermsView
from adsrental.views.adsdb import ADSDBLeadView
from adsrental.views.admin_helpers import AdminActionView
from adsrental.views.user.login import UserLoginView
from adsrental.views.user.logout import UserLogoutView
from adsrental.views.user.stats import UserStatsView
from adsrental.views.user.password import UserFixPasswordView
from adsrental.views.user.timestamps import UserTimestampsView


urlpatterns = [  # pylint: disable=C0103
    url(r'^admin_helpers/action/(?P<model_name>[A-Za-z]+)/(?P<action_name>[a-z_]+)/(?P<object_id>.+)/', AdminActionView.as_view(), name='admin_helpers_action'),
    url(r'^$', LandingView.as_view(), name='home'),
    url(r'^terms/$', TermsView.as_view(), name='terms'),
    url(r'^rdp/connect/$', RDPConnectView.as_view(), name='rdp_connect'),
    url(r'^rdp/(?P<rpid>.*)/$', RDPDownloadView.as_view(), name='rdp'),
    url(r'^thankyou/$', ThankyouView.as_view(), name='thankyou'),
    url(r'^thankyou/(?P<leadid>.*)/$', ThankyouView.as_view(), name='thankyou_email'),
    url(r'^home/$', MainView.as_view(), name='main'),
    url(r'^report/$', ReportView.as_view(), name='report'),
    url(r'^dashboard/$', DashboardView.as_view(), name='dashboard'),
    url(r'^dashboard/check_sent/$', CheckSentView.as_view(), name='dashboard_check_sent'),
    url(r'^dashboard/set_password/(?P<lead_id>.*)/$', SetPasswordView.as_view(), name='dashboard_set_password'),
    url(r'^log.php', LogView.as_view(), name='old_log'),
    url(r'^rlog.php', LogView.as_view(), name='old_rlog'),
    url(r'^keepalive.php$', StubView.as_view(), name='old_keepalive'),
    url(r'^log/$', LogView.as_view(), name='log'),
    url(r'^log/(?P<rpid>RP\d+)/$', ShowLogDirView.as_view(), name='show_log_dir'),
    url(r'^log/(?P<rpid>RP\d+)/(?P<filename>\d+\.log)$', ShowLogView.as_view(), name='show_log'),
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/login/'}, name='logout'),
    url(r'^farming/pi_config/(?P<rpid>.*)/$', PiConfigView.as_view(), name='farming_pi_config'),
    url(r'^signup/$', SignupView.as_view(), name='signup'),
    url(r'^photo/(?P<leadid>.*)/$', PhotoIdView.as_view(), name='photo_id'),
    url(r'^sf/to_shipstation/$', SFToShipstationView.as_view(), name='sf_to_shipstation'),
    url(r'^sf/launch_raspberry_pi_instance/$', SFLaunchRaspberryPiInstance.as_view(), name='sf_launch_raspberry_pi_instance'),
    url(r'^start_reverse_tunnel/(?P<rpid>.*)/$', StartReverseTunnelView.as_view(), name='start_reverse_tunnel'),
    url(r'^ec2_ssh/start_reverse_tunnel/(?P<rpid>.*)/$', StartReverseTunnelView.as_view(), name='ec2_ssh_start_reverse_tunnel'),
    url(r'^ec2_ssh/get_netstat/(?P<rpid>.*)/$', GetNetstatView.as_view(), name='ec2_ssh_get_netstat'),
    url(r'^rpi/ec2_data/(?P<rpid>.*)/$', EC2DataView.as_view(), name='rpi_ec2_data'),
    url(r'^adsdb/lead/$', ADSDBLeadView.as_view(), name='adsdb_lead'),
    url(r'^user/login/$', UserLoginView.as_view(), name='user_login'),
    url(r'^user/logout/$', UserLogoutView.as_view(), name='user_logout'),
    url(r'^user/stats/$', UserStatsView.as_view(), name='user_stats'),
    url(r'^user/stats/timestamps/$', UserTimestampsView.as_view(), name='user_timestamps'),
    url(r'^user/fix_password/$', UserFixPasswordView.as_view(), name='user_fix_password'),
    path('bundler/', include('adsrental.urls.bundler')),
    path('cron/', include('adsrental.urls.cron')),
]