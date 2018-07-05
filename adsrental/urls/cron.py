from django.urls import path

from adsrental.views.cron import SyncEC2View, LeadHistoryView, UpdatePingView, SyncDeliveredView, SyncFromShipStationView, SyncOfflineView, AutoBanView, CheckEC2View, BundlerLeadStatsCalculate


urlpatterns = [  # pylint: disable=C0103
    path('sync_from_shipstation/', SyncFromShipStationView.as_view(), name='cron_sync_from_shipstation'),
    path('sync_delivered/', SyncDeliveredView.as_view(), name='cron_sync_delivered'),
    path('sync_offline/', SyncOfflineView.as_view(), name='sync_offline'),
    path('sync_ec2/', SyncEC2View.as_view(), name='cron_sync_ec2'),
    path('lead_history/', LeadHistoryView.as_view(), name='cron_lead_history'),
    path('update_ping/', UpdatePingView.as_view(), name='cron_update_ping'),
    path('auto_ban/', AutoBanView.as_view(), name='cron_auto_ban'),
    path('check_ec2/', CheckEC2View.as_view(), name='cron_check_ec2'),
    path('bundler_lead_stat/', BundlerLeadStatsCalculate.as_view(), name='cron_bundler_lead_stat'),
]
