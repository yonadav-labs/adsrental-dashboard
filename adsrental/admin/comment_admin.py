from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from adsrental.models.comment import Comment, CommentImage

class CommentImageInline(admin.TabularInline):
    model = CommentImage
    # extra = 3


class CommentAdmin(admin.ModelAdmin):
    model = Comment
    inlines = [ CommentImageInline, ]


class CommentInline(GenericTabularInline):
    model = Comment
    # extra = 3
