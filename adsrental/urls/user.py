from django.urls import path

from adsrental.views.user.login import UserLoginView
from adsrental.views.user.logout import UserLogoutView
from adsrental.views.user.stats import UserStatsView
from adsrental.views.user.password import UserFixPasswordView
from adsrental.views.user.timestamps import UserTimestampsView


urlpatterns = [  # pylint: disable=C0103
    path('login/', UserLoginView.as_view(), name='user_login'),
    path('logout/', UserLogoutView.as_view(), name='user_logout'),
    path('stats/', UserStatsView.as_view(), name='user_stats'),
    path('stats/timestamps/', UserTimestampsView.as_view(), name='user_timestamps'),
    path('fix_password/<int:lead_account_id>/', UserFixPasswordView.as_view(), name='user_fix_password'),
]
