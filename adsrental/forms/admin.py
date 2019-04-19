
from django import forms

from adsrental.forms.extra_fields import MultiImageField
from adsrental.models.lead_account_issue import LeadAccountIssue


class ReportIssueForm(forms.Form):
    ISSUE_TYPE_CHOICES = LeadAccountIssue.ISSUE_TYPE_CHOICES

    issue_type = forms.ChoiceField(label='Issue type', choices=ISSUE_TYPE_CHOICES, required=True)
    images = MultiImageField(label='Images', required=False)
    note = forms.CharField(label='Note', required=False, widget=forms.Textarea(attrs=dict(placeholder='Add detailed notes about the issue')))


class ResolveIssueForm(forms.Form):
    images = MultiImageField(label='Images', required=False)
    note = forms.CharField(label='Note', required=False, widget=forms.Textarea(attrs=dict(placeholder='Add detailed notes about the issue')))
