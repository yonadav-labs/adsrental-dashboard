from django.core.mail import EmailMessage

from adsrental.models.lead import Lead
from adsrental.models.lead_account import LeadAccount

lead_accounts = LeadAccount.objects.filter(lead__bundler_id=137, account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK, status=LeadAccount.STATUS_AVAILABLE).exclude(note__contains='Account registration reminder email sent').exclude(lead__note__contains='Account registration reminder email sent')
print(lead_accounts.count(), 'messages will be sent')

for lead_account in lead_accounts:
    lead = lead_account.lead
    body = f'''Hi {lead.name()}. This is Adsrental! You have recently applied to rent us your social media ad space but have not completed the registration process. To get started please contact:

Chris Rageth
Text: 7853242946
Email: rageth_chris@yahoo.com
'''
    print('Sending to', lead.email)
    email = EmailMessage(
        'ATTN: Your attention needed to complete your Adsrental account registration',
        body,
        'Adsrental <noreply@adsrental.com>',
        [lead.email],
    )
    try:
        email.send()
    except:
        print('FAIL sending to', lead.email)
        continue

    lead_account.insert_note('Account registration reminder email sent')
    lead_account.save()

print(lead_accounts.count(), 'messages sent')
