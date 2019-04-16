from adsrental.models.lead_account import LeadAccount
from adsrental.models.lead_account_issue import LeadAccountIssue


for la in LeadAccount.objects.filter(wrong_password_date__isnull=False):
    lai = LeadAccountIssue.objects.filter(lead_account=la, issue_type=LeadAccountIssue.ISSUE_TYPE_WRONG_PASSWORD).first()
    if not lai:
        print(f'{la} wrong PW')
        LeadAccountIssue(
            lead_account=la,
            issue_type=LeadAccountIssue.ISSUE_TYPE_WRONG_PASSWORD,
            created=la.wrong_password_date,
        ).save()

for la in LeadAccount.objects.filter(security_checkpoint_date__isnull=False):
    lai = LeadAccountIssue.objects.filter(lead_account=la, issue_type=LeadAccountIssue.ISSUE_TYPE_SECURITY_CHECKPOINT).first()
    if not lai:
        print(f'{la} sec check')
        LeadAccountIssue(
            lead_account=la,
            issue_type=LeadAccountIssue.ISSUE_TYPE_SECURITY_CHECKPOINT,
            created=la.security_checkpoint_date,
        ).save()
