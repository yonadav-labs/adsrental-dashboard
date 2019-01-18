from django.db import models


class LeadChange(models.Model):
    '''
    Stores a single change for :model:`adsrental.Lead`, like status.
    '''

    FIELD_ADDRESS = 'address'
    FIELD_EMAIL = 'email'
    FIELD_FIRST_NAME = 'first_name'
    FIELD_LAST_NAME = 'last_name'
    FIELD_PASSWORD = 'password'
    FIELD_PI_DELIVERED = 'pi_delivered'
    FIELD_PREPARE_FOR_RESHIPMENT = 'prepare_for_reshipment'
    FIELD_SECURITY_CHECKPOINT = 'security_checkpoint'
    FIELD_STATUS = 'status'
    FIELD_WRONG_PASSWORD = 'wrong_password'

    FIELD_CHOICES = (
        (FIELD_ADDRESS, 'Address', ),
        (FIELD_EMAIL, 'Email', ),
        (FIELD_FIRST_NAME, 'First name', ),
        (FIELD_LAST_NAME, 'Last name', ),
        (FIELD_PASSWORD, 'Password', ),
        (FIELD_PI_DELIVERED, 'RPi delivered', ),
        (FIELD_PREPARE_FOR_RESHIPMENT, 'Prepare for reshipment', ),
        (FIELD_SECURITY_CHECKPOINT, 'Security checkpoint', ),
        (FIELD_STATUS, 'Status', ),
        (FIELD_WRONG_PASSWORD, 'Wrong password', ),
    )

    lead = models.ForeignKey('adsrental.Lead', on_delete=models.CASCADE)
    lead_account = models.ForeignKey('adsrental.LeadAccount', on_delete=models.CASCADE, default=None, blank=True, null=True)
    field = models.CharField(max_length=255, choices=FIELD_CHOICES)
    value = models.CharField(max_length=255)
    old_value = models.CharField(max_length=255, null=True, blank=True)
    data = models.TextField(null=True, blank=True)
    edited_by = models.ForeignKey('adsrental.User', null=True, blank=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
