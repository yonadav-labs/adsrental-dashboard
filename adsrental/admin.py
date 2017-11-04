from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Lead, RaspberryPi, EC2Instance, BrowserExtension


class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets[:-1] + (
        (
            None,
            {
                'fields': [],
            },
        ),
    )


class LeadAdmin(admin.ModelAdmin):
    model = Lead
    list_display = ('name', 'title', )
    search_fields = ['name', 'title', ]


class RaspberryPiAdmin(admin.ModelAdmin):
    model = RaspberryPi
    list_display = ('name', 'ec2_instance', 'version', 'is_deleted', )
    search_fields = ['name', 'ec2_instance__hostname', ]


class EC2InstanceAdmin(admin.ModelAdmin):
    model = EC2Instance
    list_display = ('name', 'hostname', 'is_deleted', )
    search_fields = ['name', 'hostname', ]


class BrowserExtensionAdmin(admin.ModelAdmin):
    model = EC2Instance
    list_display = ('name', 'fb_email', 'version', 'ip_address', 'status', 'created_date', )
    search_fields = ['name', ]


admin.site.register(User, CustomUserAdmin)
admin.site.register(Lead, LeadAdmin)
admin.site.register(RaspberryPi, RaspberryPiAdmin)
admin.site.register(EC2Instance, EC2InstanceAdmin)
admin.site.register(BrowserExtension, BrowserExtensionAdmin)
