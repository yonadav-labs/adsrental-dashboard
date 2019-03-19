
from django.db import models
from django.utils import timezone
from django.conf import settings


class LeadAccountIssue(models.Model):
    ISSUE_TYPE_WRONG_PASSWORD = 'Wrong Password'
    ISSUE_TYPE_SECURITY_CHECKPOINT = 'Security Checkpoint'
    ISSUE_TYPE_CONNECTION_ISSUE = 'Connection Issue'
    ISSUE_TYPE_BAN_REQUEST = 'Ban Account Request'
    ISSUE_TYPE_PHONE_NUMBER_CHANGE = 'Phone Number Change'
    ISSUE_TYPE_ADDRESS_CHANGE = 'Address Change'
    ISSUE_TYPE_RESHIPMENT_NEEDED = 'Reshipment Needed'
    ISSUE_TYPE_MISSING_PAYMENT = 'Missing Payment'
    ISSUE_TYPE_RETURNED_CHECK = 'Returned Check'
    ISSUE_TYPE_CHARGE = 'Charge to Account'
    ISSUE_TYPE_BILL_LEFT = 'Bill Left on Account'
    ISSUE_TYPE_OTHER = 'Other'

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
        (ISSUE_TYPE_OTHER, 'Other', ),
    )

    STATUS_REPORTED = 'Reported'
    STATUS_SUBMITTED = 'Submitted'
    STATUS_REJECTED = 'Rejected'
    STATUS_RESHIPPED = 'Reshipped'
    STATUS_CANCELLED = 'Cancelled'
    STATUS_VERIFIED = 'Verified'
    STATUS_PAID = 'Paid'

    STATUS_CHOICES = (
        (STATUS_REPORTED, 'Reported', ),
        (STATUS_SUBMITTED, 'Submitted', ),
        (STATUS_REJECTED, 'Rejected', ),
        (STATUS_RESHIPPED, 'Reshipped', ),
        (STATUS_CANCELLED, 'Cancelled', ),
        (STATUS_VERIFIED, 'Verified', ),
        (STATUS_PAID, 'Paid', ),
    )

    lead_account = models.ForeignKey('adsrental.LeadAccount',
                                     on_delete=models.CASCADE, related_name='lead_accounts', related_query_name='lead_account_issue')
    issue_type = models.CharField(max_length=50, choices=ISSUE_TYPE_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_REPORTED)
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

    def can_be_fixed(self):
        if self.status in [self.STATUS_REPORTED, self.STATUS_REJECTED]:
            return True

        return False

    def can_be_resolved(self):
        if self.status == self.STATUS_SUBMITTED:
            return True

        return False

    def get_time_elapsed(self):
        now = timezone.localtime(timezone.now())
        return now - self.created

    def get_old_value(self):
        if self.issue_type == self.ISSUE_TYPE_WRONG_PASSWORD:
            return self.lead_account.password  # pylint: disable=no-member
        if self.issue_type == self.ISSUE_TYPE_ADDRESS_CHANGE:
            return self.lead_account.lead.get_address()  # pylint: disable=no-member
        if self.issue_type == self.ISSUE_TYPE_PHONE_NUMBER_CHANGE:
            return self.lead_account.lead.get_phone_formatted()  # pylint: disable=no-member

        return None

    def get_note_lines(self):
        return self.note.split('\n')

    def resolve(self, edited_by):
        if not self.can_be_resolved():
            return

        if self.issue_type == self.ISSUE_TYPE_RESHIPMENT_NEEDED:
            self.status = self.STATUS_RESHIPPED
            return
        if self.issue_type == self.ISSUE_TYPE_MISSING_PAYMENT:
            self.status = self.STATUS_PAID
            return

        self.status = self.STATUS_VERIFIED
        self.insert_note(f'Resolved by {edited_by}')

    def reject(self, edited_by):
        if not self.can_be_resolved():
            return

        self.status = self.STATUS_REJECTED
        self.insert_note(f'Rejected by {edited_by}')

    def submit(self, value, edited_by):
        if not self.can_be_fixed():
            return

        self.status = self.STATUS_SUBMITTED
        self.new_value = value
        self.insert_note(f'Fix submitted by {edited_by} with value {value}')
