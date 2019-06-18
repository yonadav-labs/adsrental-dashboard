from django.contrib import admin

from adsrental.models.lead_account_issue_image import LeadAccountIssueImage


class LeadAccountIssueImageAdmin(admin.ModelAdmin):

    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }

    model = LeadAccountIssueImage
