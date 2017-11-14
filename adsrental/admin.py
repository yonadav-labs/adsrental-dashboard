from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Lead, RaspberryPi, Ec2Instance, BrowserExtension


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
    list_display = ('name', 'account_name', 'email', 'phone', 'full_address', 'tracking_number', 'online', 'tunnel_online', 'google_account', 'facebook_account', 'bundler_paid', 'wrong_password', 'last_seen', )
    search_fields = ['name', 'email', ]

    def full_address(self, obj):
        return '{}, {}, {}, {}, {}'.format(obj.street, obj.city, obj.state, obj.postal_code, obj.country)

    def tracking_number(self, obj):
        return obj.raspberry_pi.tracking_number if obj.raspberry_pi else None

    def online(self, obj):
        return obj.raspberry_pi.online if obj.raspberry_pi else False

    def tunnel_online(self, obj):
        return obj.raspberry_pi.tunnel_online if obj.raspberry_pi else False

    def last_seen(self, obj):
        return obj.raspberry_pi.last_seen if obj.raspberry_pi else False

    online.boolean = True
    tunnel_online.boolean = True


class RaspberryPiAdmin(admin.ModelAdmin):
    model = RaspberryPi
    list_display = ('name', 'version', 'links', 'is_deleted', )
    search_fields = ['name', 'ec2_instance__hostname', ]
    # list_filter = ['online', ]

    def links(self, obj):
        return ' '.join([
            '<a href="https://adsrental.com/log/{}" target="_blank">Logs</a>'.format(obj.name),
            '<a href="https://adsrental.com/rdp.php?i={}&h={}" target="_blank">RDP</a>'.format(obj.name, obj.name),
        ])

    links.allow_tags = True


class Ec2InstanceAdmin(admin.ModelAdmin):
    model = Ec2Instance
    list_display = ('name', 'hostname', 'instance_id', 'is_deleted', )
    search_fields = ['name', 'hostname', 'instance_id', ]


class BrowserExtensionAdmin(admin.ModelAdmin):
    model = BrowserExtension
    list_display = ('name', 'fb_email', 'version', 'ip_address', 'status', 'created_date', )
    search_fields = ['name', ]


admin.site.register(User, CustomUserAdmin)
admin.site.register(Lead, LeadAdmin)
admin.site.register(RaspberryPi, RaspberryPiAdmin)
admin.site.register(Ec2Instance, Ec2InstanceAdmin)
admin.site.register(BrowserExtension, BrowserExtensionAdmin)
