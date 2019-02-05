from django.urls import path

from adsrental.views.cron.sync_ec2 import SyncEC2View
from adsrental.views.cron.bundler_lead_stats_calculate import BundlerLeadStatsCalculateView
from adsrental.views.cron.lead_history import LeadHistoryView
from adsrental.views.cron.update_ping import UpdatePingView
from adsrental.views.cron.sync_delivered import SyncDeliveredView
from adsrental.views.cron.sync_from_shipstation import SyncFromShipStationView
from adsrental.views.cron.sync_offline import SyncOfflineView
from adsrental.views.cron.autoban import AutoBanView
from adsrental.views.cron.check_ec2 import CheckEC2View
from adsrental.views.cron.sync_adsdb import SyncAdsDBView
from adsrental.views.cron.fix_primary import FixPrimaryView


urlpatterns = [  # pylint: disable=C0103
    path('sync_from_shipstation/', SyncFromShipStationView.as_view(), name='cron_sync_from_shipstation'),
    path('sync_delivered/', SyncDeliveredView.as_view(), name='cron_sync_delivered'),
    path('sync_offline/', SyncOfflineView.as_view(), name='sync_offline'),
    path('sync_ec2/', SyncEC2View.as_view(), name='cron_sync_ec2'),
    path('lead_history/', LeadHistoryView.as_view(), name='cron_lead_history'),
    path('update_ping/', UpdatePingView.as_view(), name='cron_update_ping'),
    path('auto_ban/', AutoBanView.as_view(), name='cron_auto_ban'),
    path('check_ec2/', CheckEC2View.as_view(), name='cron_check_ec2'),
    path('bundler_lead_stat/', BundlerLeadStatsCalculateView.as_view(), name='cron_bundler_lead_stat'),
    path('sync_adsdb/', SyncAdsDBView.as_view(), name='cron_sync_adsdb'),
    path('fix_primary/', FixPrimaryView.as_view(), name='cron_fix_primary'),
]
