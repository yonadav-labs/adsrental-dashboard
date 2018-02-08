from __future__ import unicode_literals

from django.contrib import admin

from adsrental.models.bundler import Bundler


class BundlerAdmin(admin.ModelAdmin):
    model = Bundler
    list_display = ('id', 'name', 'utm_source', 'adsdb_id', 'email', 'phone', )
