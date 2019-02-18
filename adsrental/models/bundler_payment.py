import decimal

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

    PAYMENT_TYPES_PARENT = (
        PAYMENT_TYPE_ACCOUNT_PARENT,
        PAYMENT_TYPE_ACCOUNT_SECOND_PARENT,
    )

    BONUSES = [
        [100, decimal.Decimal(3000)],
        [90, decimal.Decimal(2500)],
        [80, decimal.Decimal(2000)],
        [70, decimal.Decimal(1500)],
        [60, decimal.Decimal(1000)],
        [50, decimal.Decimal(500)],
        [40, decimal.Decimal(400)],
        [30, decimal.Decimal(300)],
        [25, decimal.Decimal(250)],
        [20, decimal.Decimal(200)],
        [15, decimal.Decimal(150)],
        [10, decimal.Decimal(100)],
        [5, decimal.Decimal(50)],
    ]

    def __str__(self):
        return f'Bundler {self.bundler} {self.payment_type} payment for ${self.payment}'

    lead_account = models.ForeignKey('adsrental.LeadAccount', on_delete=models.SET_NULL, null=True)
    bundler = models.ForeignKey('adsrental.Bundler', on_delete=models.SET_NULL, null=True, db_index=True)
    payment = models.DecimalField(max_digits=8, decimal_places=2)
    payment_type = models.CharField(max_length=50, choices=PAYMENT_TYPE_CHOICES, default=PAYMENT_TYPE_ACCOUNT_MAIN, db_index=True)
    report = models.ForeignKey('adsrental.BundlerPaymentsReport', on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    datetime = models.DateTimeField(default=timezone.now)
    paid = models.BooleanField(default=False, db_index=True)
    ready = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
