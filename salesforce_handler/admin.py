from django.contrib import admin
from django.core.urlresolvers import reverse
from django.contrib.humanize.templatetags.humanize import naturaltime

from .models import Lead, RaspberryPi, Ec2Instance, BrowserExtension


class LeadAdmin(admin.ModelAdmin):
    model = Lead
    # list_select_related = (
    #     'raspberry_pi',
    # )
    list_display = ('id', 'name', 'account_name', 'email_field', 'phone', 'full_address', 'tracking_number', 'online', 'tunnel_online', 'google_account', 'facebook_account', 'utm_source', 'bundler_paid', 'wrong_password', 'last_seen', )
    search_fields = ['name', 'email', 'account_name', ]

    def email_field(self, obj):
        return '{} (<a href="{}?q={}" target="_blank">Local</a>)'.format(
            obj.email,
            reverse('admin:adsrental_lead_changelist'),
            obj.email,
        )

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(LeadAdmin, self).get_search_results(request, queryset, search_term)

        if request.user.utm_source:
            queryset |= self.model.objects.filter(utm_source=request.user.utm_source)
        return queryset, use_distinct

    def full_address(self, obj):
        return '{}, {}, {}, {}, {}'.format(obj.street, obj.city, obj.state, obj.postal_code, obj.country)

    def tracking_number(self, obj):
        return obj.raspberry_pi.tracking_number if obj.raspberry_pi else None

    def online(self, obj):
        return obj.raspberry_pi.online if obj.raspberry_pi else False

    def tunnel_online(self, obj):
        return obj.raspberry_pi.tunnel_online if obj.raspberry_pi else False

    def last_seen(self, obj):
        if obj.raspberry_pi is None or obj.raspberry_pi.last_seen is None:
            return None

        last_seen = obj.raspberry_pi.last_seen

        return u'<span title="{}">{}</span>'.format(last_seen, naturaltime(last_seen))

    last_seen.allow_tags = True
    email_field.allow_tags = True
    email_field.short_description = 'Email'
    email_field.admin_order_field = 'email'
    online.boolean = True
    tunnel_online.boolean = True


class RaspberryPiAdmin(admin.ModelAdmin):
    model = RaspberryPi
    list_display = ('name', 'version', 'online', 'tunnel_online', 'links', 'is_deleted', 'last_seen', )
    search_fields = ['name', ]
    list_filter = ['online', ]

    def links(self, obj):
        return ' '.join([
            '<a href="/log/{}" target="_blank">Logs</a>'.format(obj.name),
            '<a href="/rdp.php?i={}&h={}" target="_blank">RDP</a>'.format(obj.name, obj.name),
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


admin.site.register(Lead, LeadAdmin)
admin.site.register(RaspberryPi, RaspberryPiAdmin)
admin.site.register(Ec2Instance, Ec2InstanceAdmin)
admin.site.register(BrowserExtension, BrowserExtensionAdmin)
