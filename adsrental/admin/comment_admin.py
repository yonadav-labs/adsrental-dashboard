from django.contrib import admin

from adsrental.models.lead import Comment, CommentImage

class CommentImageInline(admin.TabularInline):
    model = CommentImage
    extra = 3

class CommentAdmin(admin.ModelAdmin):

    model = Comment

    inlines = [ CommentImageInline, ]
