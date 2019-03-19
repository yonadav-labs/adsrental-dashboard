
from django import forms

from adsrental.models.lead_account_issue import LeadAccountIssue


class BundlerIssuesForm(forms.Form):
    ISSUE_TYPE_CHOICES = (
        ('', 'All'),
    ) + LeadAccountIssue.ISSUE_TYPE_CHOICES
    STATUS_CHOICES = (
        ('', 'All'),
        (LeadAccountIssue.STATUS_REPORTED, 'Reported'),
        (LeadAccountIssue.STATUS_REJECTED, 'Rejected'),
        (LeadAccountIssue.STATUS_SUBMITTED, 'Submitted'),
    )

    issue_type = forms.ChoiceField(label='Issue type', choices=ISSUE_TYPE_CHOICES, required=False)
    status = forms.ChoiceField(label='Status', choices=STATUS_CHOICES, required=False)

    def filter(self, queryset):
        if self.cleaned_data['issue_type']:
            queryset = queryset.filter(issue_type=self.cleaned_data['issue_type'])
        if self.cleaned_data['status']:
            queryset = queryset.filter(status=self.cleaned_data['status'])

        return queryset


class FixIssueForm(forms.Form):
    old_value = forms.CharField(label='Old value', required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    new_value = forms.CharField(label='New value', required=True)
