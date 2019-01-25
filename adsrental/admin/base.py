from django.contrib import admin


class ReadOnlyModelAdmin(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        super(ReadOnlyModelAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = None

    def has_add_permission(self, request):
        return False

    # def has_change_permission(self, request, obj=None):
    #     return False
