from django.views import View

from adsrental.models.signals import slack_daily_account_issues
from adsrental.models.lead_account_issue import LeadAccountIssue


class DailyAccountStatusView(View):

    def get(self, request):
        for issue_type in [LeadAccountIssue.ISSUE_TYPE_WRONG_PASSWORD, 
                           LeadAccountIssue.ISSUE_TYPE_SECURITY_CHECKPOINT,
                           LeadAccountIssue.ISSUE_TYPE_CONNECTION_ISSUE,
                           LeadAccountIssue.ISSUE_TYPE_OFFLINE]:
            issues = LeadAccountIssue.objects.filter(issue_type=issue_type) \
                                             .filter(status__in=[LeadAccountIssue.STATUS_REPORTED,
                                                                 LeadAccountIssue.STATUS_SUBMITTED,
                                                                 LeadAccountIssue.STATUS_REJECTED]) \
                                             .order_by(lead_account_id) \
                                             .exclude(lead_account__lead__bundler__slack_tag__isnull=True) \
                                             .exclude(lead_account__lead__bundler__slack_tag__exact='')

            issues_ = []
            prev_to = None

            for issue in issues:
                to = issue.lead_account.lead
                if prev_to != to:
                    if issues_:
                        slack_daily_account_issues(prev_to, issue_type, issues_)
                    prev_to = to
                    issues_ = [issue]
                else:
                    issues_.append(issue)
