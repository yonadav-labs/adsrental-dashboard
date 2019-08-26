from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Comment(models.Model):
    "Coments class for Lead, LeadAccount, LeadAccountIssue"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="comments", null=True, blank=True)
    text = models.TextField(
        blank=True, null=True,
        help_text='Not shown when you hover user name in admin interface.')
    response = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    content_object = GenericForeignKey()

    def __str__(self):
        if not self.user:
            return 'User'

        if self.user.is_superuser:
            return 'Admin'

        return f'{self.user.first_name} {self.user.last_name}'

    def get_username(self):
        if not self.user:
            return 'User'

        if self.user.is_superuser:
            return 'Admin'

        return f'{self.user.first_name} {self.user.last_name}'


class CommentImage(models.Model):
    "Images for comment"

    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    image = models.ImageField(blank=True, null=True)
