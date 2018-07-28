from django.urls import path

from adsrental.views.rdp.ec2_rdp_file import EC2RDPFileView
from adsrental.views.rdp.ec2_connect import EC2ConnectView
from adsrental.views.rdp.vultr_connect import VultrConnectView
from adsrental.views.rdp.vultr_rdp_file import VultrRDPFileView


urlpatterns = [
    path('ec2/<rpid>/connect/', EC2ConnectView.as_view(), name='rdp_ec2_connect'),
    path('ec2/<rpid>/connect/<action>/', EC2ConnectView.as_view(), name='rdp_ec2_connect'),
    path('ec2/<rpid>/file/', EC2RDPFileView.as_view(), name='rdp_ec2_file'),
    path('vultr/<int:vultr_instance_id>/connect/', VultrConnectView.as_view(), name='rdp_vultr_connect'),
    path('vultr/<int:vultr_instance_id>/connect/<action>/', VultrConnectView.as_view(), name='rdp_vultr_connect'),
    path('vultr/<int:vultr_instance_id>/file/', VultrRDPFileView.as_view(), name='rdp_vultr_file'),
]
