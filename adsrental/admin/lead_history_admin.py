from __future__ import unicode_literals

from django.contrib import admin

from adsrental.models.lead_history import LeadHistory


class LeadHistoryAdmin(admin.ModelAdmin):
    model = LeadHistory
    list_display = ('id', 'lead', 'date', 'checks_offline', 'checks_online', 'checks_wrong_password', )
