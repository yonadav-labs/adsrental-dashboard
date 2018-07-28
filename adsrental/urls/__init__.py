import django.contrib.auth.views as auth_views
from django.urls import include, path

from adsrental.views.log import LogView, ShowLogDirView, ShowLogView
from adsrental.views.main import MainView
from adsrental.views.stub import StubView
from adsrental.views.thankyou import ThankyouView
from adsrental.views.report import ReportView
from adsrental.views.farming import PiConfigView
from adsrental.views.signup import SignupView
from adsrental.views.photo_id import PhotoIdView
from adsrental.views.sf import SFToShipstationView, SFLaunchRaspberryPiInstance
from adsrental.views.ec2_ssh import StartReverseTunnelView, GetNetstatView
from adsrental.views.rpi import EC2DataView
from adsrental.views.landing import LandingView, TermsView
from adsrental.views.adsdb import ADSDBLeadView
from adsrental.views.admin_helpers import AdminActionView
from adsrental.views.robots import RobotsView


urlpatterns = [
    path('admin_helpers/action/<model_name>/<action_name>/<object_id>/', AdminActionView.as_view(), name='admin_helpers_action'),
    path('', LandingView.as_view(), name='home'),
    path('terms/', TermsView.as_view(), name='terms'),
    path('thankyou/', ThankyouView.as_view(), name='thankyou'),
    path('thankyou.php', ThankyouView.as_view(), name='thankyou'),
    path('thankyou/<leadid>/', ThankyouView.as_view(), name='thankyou_email'),
    path('home/', MainView.as_view(), name='main'),
    path('report/', ReportView.as_view(), name='report'),
    path('log.php', LogView.as_view(), name='old_log'),
    path('rlog.php', LogView.as_view(), name='old_rlog'),
    path('keepalive.php', StubView.as_view(), name='old_keepalive'),
    path('log/', LogView.as_view(), name='log'),
    path('log/<rpid>/', ShowLogDirView.as_view(), name='show_log_dir'),
    path('log/<rpid>/<filename>', ShowLogView.as_view(), name='show_log'),
    path('login/', auth_views.login, {'template_name': 'login.html'}, name='login'),
    path('logout/', auth_views.logout, {'next_page': '/login/'}, name='logout'),
    path('farming/pi_config/<rpid>/', PiConfigView.as_view(), name='farming_pi_config'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('photo/<leadid>/', PhotoIdView.as_view(), name='photo_id'),
    path('sf/to_shipstation/', SFToShipstationView.as_view(), name='sf_to_shipstation'),
    path('sf/launch_raspberry_pi_instance/', SFLaunchRaspberryPiInstance.as_view(), name='sf_launch_raspberry_pi_instance'),
    path('start_reverse_tunnel/<rpid>/', StartReverseTunnelView.as_view(), name='start_reverse_tunnel'),
    path('ec2_ssh/start_reverse_tunnel/<rpid>/', StartReverseTunnelView.as_view(), name='ec2_ssh_start_reverse_tunnel'),
    path('ec2_ssh/get_netstat/<rpid>/', GetNetstatView.as_view(), name='ec2_ssh_get_netstat'),
    path('rpi/ec2_data/<rpid>/', EC2DataView.as_view(), name='rpi_ec2_data'),
    path('adsdb/lead/', ADSDBLeadView.as_view(), name='adsdb_lead'),
    path('rdp/', include('adsrental.urls.rdp')),
    path('bundler/', include('adsrental.urls.bundler')),
    path('cron/', include('adsrental.urls.cron')),
    path('user/', include('adsrental.urls.user')),
    path('dashboard/', include('adsrental.urls.dashboard')),
    path('bookkeeper/', include('adsrental.urls.bookkeeper')),
    path('robots.txt', RobotsView.as_view(), name='robots'),
]
