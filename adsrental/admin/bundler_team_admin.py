from django.contrib import admin

from adsrental.models.bundler_team import BundlerTeam
from adsrental.admin.base import CSVExporter


class BundlerTeamAdmin(admin.ModelAdmin, CSVExporter):
    model = BundlerTeam
    csv_fields = (
        'id',
        'name',
        'created',
    )

    csv_titles = (
        'Id',
        'Name',
        'Created',
    )
    list_display = (
        'id',
        'name',
        'created',
    )
    search_fields = ('name', )
    actions = ('export_as_csv',)
