from django.contrib import admin

from adsrental.models.bundler_team import BundlerTeam


class BundlerTeamAdmin(admin.ModelAdmin):
    model = BundlerTeam
    list_display = (
        'id',
        'name',
        'created',
    )
    search_fields = ('name', )
