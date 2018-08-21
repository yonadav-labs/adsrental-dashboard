'Urls for bundler dasboard'
from django.urls import path

from adsrental.views.dashboard.home import DashboardHomeView
from adsrental.views.dashboard.change_password import ChangePasswordView
from adsrental.views.dashboard.change_address import ChangeAddressView
from adsrental.views.dashboard.disqualify_lead_account import DisqualifyLeadAccountView
from adsrental.views.dashboard.photo_id import PhotoIDVIew


urlpatterns = [
    path('', DashboardHomeView.as_view(), name='dashboard'),
    path('set_password/<int:lead_account_id>/', ChangePasswordView.as_view(), name='dashboard_set_password'),
    path('change_address/<lead_id>/', ChangeAddressView.as_view(), name='dashboard_change_address'),
    path('disqualify/<lead_account_id>/', DisqualifyLeadAccountView.as_view(), name='dashboard_disqualify'),
    path('photo/<lead_id>/', PhotoIDVIew.as_view(), name='dashboard_photo'),
]
