from django.urls import path

from adsrental.views.slack.stats import StatsView


urlpatterns = [
    path('stats/', StatsView.as_view(), name='stats'),
]
