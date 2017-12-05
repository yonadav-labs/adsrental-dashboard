import datetime

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils import timezone
from django.contrib.admin import SimpleListFilter

from adsrental.models.user import User
from adsrental.models.legacy import Lead, RaspberryPi


class OnlineListFilter(SimpleListFilter):
    title = 'EC2 online state'
    parameter_name = 'online'

    def lookups(self, request, model_admin):
        return (
            ('online', 'Online only'),
            ('offline', 'Offline only'),
            ('offline_2days', 'Offline for last 2 days'),
            ('offline_5days', 'Offline for last 5 days'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'online':
            return queryset.filter(raspberry_pi__last_seen__gt=timezone.now() - datetime.timedelta(hours=14))
        if self.value() == 'offline':
            return queryset.filter(raspberry_pi__last_seen__lte=timezone.now() - datetime.timedelta(hours=14))
        if self.value() == 'offline_2days':
            return queryset.filter(raspberry_pi__last_seen__lte=timezone.now() - datetime.timedelta(hours=14 + 2 * 24))
        if self.value() == 'offline_5days':
            return queryset.filter(raspberry_pi__last_seen__lte=timezone.now() - datetime.timedelta(hours=14 + 5 * 24))


class TunnelOnlineListFilter(SimpleListFilter):
    title = 'Tunnel online state'
    parameter_name = 'tunnel_online'

    def lookups(self, request, model_admin):
        return (
            ('online', 'Online only'),
            ('offline', 'Offline only'),
            ('offline_2days', 'Offline for last 2 days'),
            ('offline_5days', 'Offline for last 5 days'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'online':
            return queryset.filter(raspberry_pi__tunnel_last_tested__gt=timezone.now() - datetime.timedelta(hours=14))
        if self.value() == 'offline':
            return queryset.filter(raspberry_pi__tunnel_last_tested__lte=timezone.now() - datetime.timedelta(hours=14))
        if self.value() == 'offline_2days':
            return queryset.filter(raspberry_pi__tunnel_last_tested__lte=timezone.now() - datetime.timedelta(hours=14 + 2 * 24))
        if self.value() == 'offline_5days':
            return queryset.filter(raspberry_pi__tunnel_last_tested__lte=timezone.now() - datetime.timedelta(hours=14 + 5 * 24))


class WrongPasswordListFilter(SimpleListFilter):
    title = 'Wrong Password'
    parameter_name = 'wrong_password'

    def lookups(self, request, model_admin):
        return (
            ('no', 'No'),
            ('yes', 'Yes'),
            ('yes_2days', 'Yes for 2 days'),
            ('yes_5days', 'Yes for 5 days'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'no':
            return queryset.filter(wrong_password=False)
        if self.value() == 'yes':
            return queryset.filter(wrong_password=True)
        if self.value() == 'yes_2days':
            return queryset.filter(wrong_password=True, raspberry_pi__last_seen__lte=timezone.now() - datetime.timedelta(hours=14 + 2 * 24))
        if self.value() == 'yes_5days':
            return queryset.filter(wrong_password=True, raspberry_pi__last_seen__lte=timezone.now() - datetime.timedelta(hours=14 + 5 * 24))


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
    list_display = ('leadid', 'name', 'email', 'phone', 'google_account', 'facebook_account', 'raspberry_pi', 'first_seen', 'last_seen', 'tunnel_last_tested', 'online', 'tunnel_online', 'wrong_password', 'pi_delivered', 'bundler_paid')
    list_filter = (OnlineListFilter, TunnelOnlineListFilter, WrongPasswordListFilter, 'utm_source', 'bundler_paid', 'pi_delivered', )
    select_related = ('raspberry_pi', )
    search_fields = ('leadid', 'first_name', 'last_name', 'raspberry_pi__rpid', )

    def name(self, obj):
        return '{} {}'.format(obj.first_name, obj.last_name)

    def online(self, obj):
        return obj.raspberry_pi.online()

    def tunnel_online(self, obj):
        return obj.raspberry_pi.tunnel_online()

    def first_seen(self, obj):
        if obj.raspberry_pi.first_seen is None:
            return None

        return naturaltime(obj.raspberry_pi.first_seen + datetime.timedelta(hours=7))

    def last_seen(self, obj):
        if obj.raspberry_pi.last_seen is None:
            return None

        return naturaltime(obj.raspberry_pi.last_seen + datetime.timedelta(hours=7))

    def tunnel_last_tested(self, obj):
        if obj.raspberry_pi.tunnel_last_tested is None:
            return None

        return naturaltime(obj.raspberry_pi.tunnel_last_tested + datetime.timedelta(hours=7))

    online.boolean = True
    tunnel_online.boolean = True


class RaspberryPiAdmin(admin.ModelAdmin):
    model = RaspberryPi
    list_display = ('rpid', 'leadid', 'ipaddress', 'ec2_hostname', 'first_seen', 'last_seen', 'tunnel_last_tested', )
    search_fields = ('leadid', 'rpid', 'ec2_hostname', )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Lead, LeadAdmin)
admin.site.register(RaspberryPi, RaspberryPiAdmin)
