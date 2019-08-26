import unicodecsv as csv

from django.contrib import admin
from django.utils import timezone
from django.db.models.sql.where import WhereNode
from django.http import HttpResponse


class EverythingNode:
    pass


class ReadOnlyModelAdmin(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        super(ReadOnlyModelAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # def has_change_permission(self, request, obj=None):
    #     return False


class CSVExporter():
    csv_fields = []
    csv_titles = []
    csv_filename = 'report__{month}_{year}.csv'

    def export_as_csv(self, request, queryset):
        field_names = self.csv_fields
        field_titles = self.csv_titles if self.csv_titles else self.csv_fields

        if queryset.count() > 50:
            new_where = WhereNode(children=queryset.query.where.children[:-1])
            queryset.query.where = new_where
            queryset = queryset.all()

        date = timezone.localtime(timezone.now()).date()

        response = HttpResponse(content_type='text/csv')
        filename = self.csv_filename.format(
            day=date.strftime('%d'),
            month=date.strftime('%b').lower(),
            year=date.strftime('%Y'),
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'

        writer = csv.writer(response, encoding='utf-8')
        writer.writerow(field_titles)
        for obj in queryset:
            row = []
            for field in field_names:
                if hasattr(self, field) and callable(getattr(self, field)):
                    row.append(getattr(self, field)(obj))
                    continue
                if hasattr(obj, field) and callable(getattr(obj, field)):
                    row.append(getattr(obj, field)())
                    continue

                item = obj
                for subfield in field.split('__'):
                    if hasattr(item, subfield):
                        if callable(getattr(item, subfield)):
                            item = getattr(item, subfield)()
                        else:
                            item = getattr(item, subfield)
                    else:
                        item = None
                        break
                row.append(item)
            writer.writerow(row)
        return response
