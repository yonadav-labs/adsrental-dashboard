from django.db import models
from django.utils import timezone


class BundlerPayment(models.Model):
    PAYMENT_TYPE_ACCOUNT_MAIN = 'account'
    PAYMENT_TYPE_ACCOUNT_CHARGEBACK = 'chargeback'
    PAYMENT_TYPE_ACCOUNT_PARENT = 'account_parent'
    PAYMENT_TYPE_ACCOUNT_SECOND_PARENT = 'account_second_parent'
    PAYMENT_TYPE_BONUS = 'bonus'
    PAYMENT_TYPE_CHOICES = (
        (PAYMENT_TYPE_ACCOUNT_MAIN, 'Lead account activated'),
        (PAYMENT_TYPE_ACCOUNT_PARENT, 'Child\'s Lead account activated'),
        (PAYMENT_TYPE_ACCOUNT_SECOND_PARENT, 'Child\'s Lead account activated (2nd parent)'),
        (PAYMENT_TYPE_BONUS, 'Bonus'),
        (PAYMENT_TYPE_ACCOUNT_CHARGEBACK, 'Chargeback'),
    )
    lead_account = models.ForeignKey('adsrental.LeadAccount', on_delete=models.SET_NULL, null=True)
    bundler = models.ForeignKey('adsrental.Bundler', on_delete=models.SET_NULL, null=True)
    payment = models.DecimalField(max_digits=8, decimal_places=2)
    payment_type = models.CharField(max_length=50, choices=PAYMENT_TYPE_CHOICES, default=PAYMENT_TYPE_ACCOUNT_MAIN)
    report = models.ForeignKey('adsrental.BundlerPaymentsReport', on_delete=models.SET_NULL, null=True, blank=True)
    datetime = models.DateTimeField(default=timezone.now)
    paid = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
