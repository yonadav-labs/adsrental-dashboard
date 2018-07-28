from django.urls import path

from adsrental.views.rdp import RDPDownloadView, RDPConnectView
from adsrental.views.rdp.vultr_connect import VultrConnectView
from adsrental.views.rdp.vultr_rdp_file import VultrRDPFileView


urlpatterns = [
    path('connect/', RDPConnectView.as_view(), name='rdp_connect'),
    path('<rpid>/', RDPDownloadView.as_view(), name='rdp'),
    path('vultr/<int:vultr_instance_id>/connect/', VultrConnectView.as_view(), name='rdp_vultr_connect'),
    path('vultr/<int:vultr_instance_id>/connect/<action>/', VultrConnectView.as_view(), name='rdp_vultr_connect'),
    path('vultr/<int:vultr_instance_id>/file/', VultrRDPFileView.as_view(), name='rdp_vultr_file'),
]
