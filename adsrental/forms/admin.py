
from django import forms

from adsrental.models.lead_account_issue import LeadAccountIssue


class ReportIssueForm(forms.Form):
    ISSUE_TYPE_CHOICES = LeadAccountIssue.ISSUE_TYPE_CHOICES

    issue_type = forms.ChoiceField(label='Issue type', choices=ISSUE_TYPE_CHOICES, required=True)
