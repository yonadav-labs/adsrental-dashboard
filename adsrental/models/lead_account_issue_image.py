from django.db import models
from django.utils import timezone


class LeadAccountIssueImage(models.Model):
    lead_account_issue = models.ForeignKey('adsrental.LeadAccountIssue', on_delete=models.CASCADE, related_name='images', related_query_name='image')
    image = models.ImageField(blank=True, null=True)
    created = models.DateTimeField(default=timezone.now)
