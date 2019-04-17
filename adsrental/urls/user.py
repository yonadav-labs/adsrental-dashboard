from django.urls import path

from adsrental.views.user.login import UserLoginView
from adsrental.views.user.logout import UserLogoutView
from adsrental.views.user.stats import UserStatsView, AdminUserStatsView
from adsrental.views.user.actions import FixLeadAccountIssueView
from adsrental.views.user.timestamps import UserTimestampsView


urlpatterns = [  # pylint: disable=C0103
    path('login/', UserLoginView.as_view(), name='user_login'),
    path('logout/', UserLogoutView.as_view(), name='user_logout'),
    path('stats/', UserStatsView.as_view(), name='user_stats'),
    path('stats/timestamps/', UserTimestampsView.as_view(), name='user_timestamps'),
    path('stats/rpid/<rpid>/', AdminUserStatsView.as_view(), name='admin_user_stats'),
    path('fix/<int:lead_account_issue_id>/', FixLeadAccountIssueView.as_view(), name='user_fix_lead_account_issue'),
]
