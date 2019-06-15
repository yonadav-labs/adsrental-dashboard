from django.contrib import admin

from adsrental.models.lead_account_issue_image import LeadAccountIssueImage
from adsrental.admin.base import CSVExporter


class LeadAccountIssueImageAdmin(admin.ModelAdmin, CSVExporter):
    csv_fields = (
        'id',
    )

    csv_titles = (
        'ID',
    )

    actions = ('export_as_csv',)

    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }

    model = LeadAccountIssueImage
