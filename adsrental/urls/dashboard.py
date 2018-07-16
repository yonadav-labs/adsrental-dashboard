from django.urls import path

from adsrental.views.dashboard.home import DashboardHomeView
from adsrental.views.dashboard.change_password import ChangePasswordView
from adsrental.views.dashboard.change_address import ChangeAddressView
from adsrental.views.dashboard.update_shipstation import UpdateShipstationView


urlpatterns = [  # pylint: disable=C0103
    path('', DashboardHomeView.as_view(), name='dashboard'),
    path('set_password/<int:lead_account_id>/', ChangePasswordView.as_view(), name='dashboard_set_password'),
    path('change_address/<lead_id>/', ChangeAddressView.as_view(), name='dashboard_change_address'),
    path('update_shipstation/<lead_id>/', UpdateShipstationView.as_view(), name='dashboard_update_shipstation'),
]
