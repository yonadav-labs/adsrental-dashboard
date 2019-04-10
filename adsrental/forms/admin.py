
from django import forms

from adsrental.models.lead_account_issue import LeadAccountIssue


class ReportIssueForm(forms.Form):
    ISSUE_TYPE_CHOICES = LeadAccountIssue.ISSUE_TYPE_CHOICES

    issue_type = forms.ChoiceField(label='Issue type', choices=ISSUE_TYPE_CHOICES, required=True)
    image = forms.ImageField(label='Image', required=False)
    note = forms.CharField(label='Note', required=False, widget=forms.Textarea(attrs=dict(placeholder='Add detailed notes about the issue')))
