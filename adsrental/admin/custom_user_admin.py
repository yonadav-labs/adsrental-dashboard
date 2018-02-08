
from __future__ import unicode_literals

from django.contrib.auth.admin import UserAdmin

from adsrental.models.user import User


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
