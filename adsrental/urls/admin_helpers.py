from django.urls import path

from adsrental.views.admin_helpers import AdminActionView
from adsrental.views.admin.bundler_bonuses import AdminBundlerBonusesView
from adsrental.views.admin.bundler_daily_bonuses import AdminBundlerDailyBonusesView
from adsrental.views.admin.bundler_bonuses_accounts import AdminBundlerBonusesAccountsView


urlpatterns = [  # pylint: disable=C0103
    path('action/<model_name>/<action_name>/<object_id>/', AdminActionView.as_view(), name='action'),
    path('bundler_bonuses/', AdminBundlerBonusesView.as_view(), name='bundler_bonuses'),
    path('bundler_bonuses/daily/', AdminBundlerDailyBonusesView.as_view(), name='bundler_daily_bonuses'),
    path('bundler_bonuses/<int:bundler_id>/', AdminBundlerBonusesAccountsView.as_view(), name='bundler_bonuses_accounts'),
]
