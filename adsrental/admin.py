from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from adsrental.models.user import User
from adsrental.models.legacy import Lead, RaspberryPi


class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets[:-1] + (
        (
            None,
            {
                'fields': [
                    'utm_source',
                ],
            },
        ),
    )


class LeadAdmin(admin.ModelAdmin):
    model = Lead
    list_display = ('leadid', 'first_name', 'last_name', 'email', 'phone', 'google_account', 'facebook_account', 'raspberry_pi', )


class RaspberryPiAdmin(admin.ModelAdmin):
    model = RaspberryPi
    list_display = ('rpid', 'leadid', 'ipaddress', 'ec2_hostname', 'first_seen', 'last_seen', 'tunnel_last_tested', )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Lead, LeadAdmin)
admin.site.register(RaspberryPi, RaspberryPiAdmin)
