from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.safestring import mark_safe

from adsrental.models.user import User
from adsrental.admin.base import CSVExporter


class CustomUserAdmin(UserAdmin, CSVExporter):
    model = User
    csv_fields = (
        'id',
    )

    csv_titles = (
        'ID',
    )
    fieldsets = UserAdmin.fieldsets[:-1] + (
        (
            None,
            {
                'fields': [
                    'bundler',
                    'allowed_raspberry_pis',
                ],
            },
        ),
    )
    filter_horizontal = ('groups', 'user_permissions', 'allowed_raspberry_pis', )
    list_filter = UserAdmin.list_filter + (
        'bundler',
    )
    list_display = UserAdmin.list_display + (
        'bundler_field',
    )
    actions = UserAdmin.actions + [
        'export_as_csv',
    ]

    def bundler_field(self, obj):
        if not obj.bundler:
            return None
        return mark_safe('<a href="{url}?q={q}" title="{title}">{text}</a>'.format(
            url=reverse('admin:adsrental_bundler_changelist'),
            q=obj.bundler.email,
            title=obj.bundler.utm_source,
            text=obj.bundler,
        ))

    bundler_field.short_description = 'bundler'
