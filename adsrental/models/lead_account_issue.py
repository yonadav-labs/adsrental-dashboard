
from django.db import models
from django.utils import timezone
from django.conf import settings


class LeadAccountIssue(models.Model):
    ISSUE_TYPE_BAN_REQUEST = 'Ban Account Request'
    ISSUE_TYPE_CONNECTION_ISSUE = 'Connection Issue'
    ISSUE_TYPE_WRONG_PASSWORD = 'Wrong Password'
    ISSUE_TYPE_SECURITY_CHECKPOINT = 'Security Checkpoint'
    ISSUE_TYPE_PHONE_NUMBER_CHANGE = 'Phone Number Change'
    ISSUE_TYPE_ADDRESS_CHANGE = 'Address Change'
    ISSUE_TYPE_RESHIPMENT_NEEDED = 'Reshipment Needed'
    ISSUE_TYPE_MISSING_PAYMENT = 'Missing Payment'
    ISSUE_TYPE_RETURNED_CHECK = 'Returned Check'
    ISSUE_TYPE_CHARGE = 'Charge to Account'
    ISSUE_TYPE_BILL_LEFT = 'Bill Left on Account'

    ISSUE_TYPE_CHOICES = (
        (ISSUE_TYPE_BAN_REQUEST, 'Ban Account Request', ),
        (ISSUE_TYPE_CONNECTION_ISSUE, 'Connection Issue', ),
        (ISSUE_TYPE_WRONG_PASSWORD, 'Wrong Password', ),
        (ISSUE_TYPE_SECURITY_CHECKPOINT, 'Security Checkpoint', ),
        (ISSUE_TYPE_PHONE_NUMBER_CHANGE, 'Phone Number Change', ),
        (ISSUE_TYPE_ADDRESS_CHANGE, 'Address Change', ),
        (ISSUE_TYPE_RESHIPMENT_NEEDED, 'Reshipment Needed', ),
        (ISSUE_TYPE_MISSING_PAYMENT, 'Missing Payment', ),
        (ISSUE_TYPE_RETURNED_CHECK, 'Returned Check', ),
        (ISSUE_TYPE_CHARGE, 'Charge to Account', ),
        (ISSUE_TYPE_BILL_LEFT, 'Bill Left on Account', ),
    )

    STATUS_OPEN = 'Open'
    STATUS_CLOSED = 'Closed'

    STATUS_CHOICES = (
        (STATUS_OPEN, 'Open'),
        (STATUS_CLOSED, 'Closed'),
    )

    lead_account = models.ForeignKey('adsrental.LeadAccount',
                                     on_delete=models.CASCADE, related_name='lead_accounts', related_query_name='lead_account_issue')
    issue_type = models.CharField(max_length=50, choices=ISSUE_TYPE_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_OPEN)
    note = models.TextField(default='', blank=True)
    new_value = models.TextField(default='', blank=True)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)

    def insert_note(self, message, event_datetime=None):
        'Add a text message to note field'
        if not event_datetime:
            event_datetime = timezone.localtime(timezone.now())

        line = f'{event_datetime.strftime(settings.SYSTEM_DATETIME_FORMAT)} {message}'

        if not self.note:
            self.note = line
        else:
            self.note = f'{self.note}\n{line}'
