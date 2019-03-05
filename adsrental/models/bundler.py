import decimal

from django.db import models


class Bundler(models.Model):
    '''
    Stores a single bundler entry, used to get bundler info for lead by *utm_source*
    '''
    PAYMENT = decimal.Decimal(150.00)
    CHARGEBACK_PAYMENT = decimal.Decimal(50.00)

    name = models.CharField(max_length=255, unique=True, db_index=True)
    utm_source = models.CharField(max_length=50, db_index=True, null=True, blank=True)
    adsdb_id = models.IntegerField(null=True, blank=True, help_text='ID from adsdb database')
    email = models.CharField(max_length=255, null=True, blank=True)
    skype = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    bank_info = models.TextField(null=True, blank=True)
    slack_tag = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True, help_text='If inactive, landing/sugnup page will not be shown for this utm_source.')
    enable_chargeback = models.BooleanField(default=True, help_text='If inactive, no chargeback will be calculated for lead accounts.')
    facebook_payment = models.DecimalField(default=decimal.Decimal(125.00), max_digits=8, decimal_places=2, help_text='Payout for Facebook accounts')
    facebook_screenshot_payment = models.DecimalField(default=decimal.Decimal(125.00), max_digits=8, decimal_places=2, help_text='Payout for Facebook Screenshot accounts')
    google_payment = models.DecimalField(default=decimal.Decimal(125.00), max_digits=8, decimal_places=2, help_text='Payout for Google accounts')
    amazon_payment = models.DecimalField(default=decimal.Decimal(60.00), max_digits=8, decimal_places=2, help_text='Payout for Amazon accounts')
    facebook_parent_payment = models.DecimalField(default=decimal.Decimal(0.00), max_digits=8, decimal_places=2, help_text='Amount to withdraw from lead payment to be paid to parent bundler.')
    facebook_screenshot_parent_payment = models.DecimalField(default=decimal.Decimal(0.00), max_digits=8, decimal_places=2, help_text='Amount to withdraw from lead payment to be paid to parent bundler.')
    google_parent_payment = models.DecimalField(default=decimal.Decimal(0.00), max_digits=8, decimal_places=2, help_text='Amount to withdraw from lead payment to be paid to parent bundler.')
    amazon_parent_payment = models.DecimalField(default=decimal.Decimal(0.00), max_digits=8, decimal_places=2, help_text='Amount to withdraw from lead payment to be paid to parent bundler.')
    facebook_second_parent_payment = models.DecimalField(default=decimal.Decimal(0.00), max_digits=8, decimal_places=2, help_text='Amount to withdraw from lead payment to be paid to second parent bundler.')
    facebook_screenshot_second_parent_payment = models.DecimalField(default=decimal.Decimal(0.00), max_digits=8, decimal_places=2, help_text='Amount to withdraw from lead payment to be paid to parent bundler.')
    google_second_parent_payment = models.DecimalField(default=decimal.Decimal(0.00), max_digits=8, decimal_places=2, help_text='Amount to withdraw from lead payment to be paid to second parent bundler.')
    amazon_second_parent_payment = models.DecimalField(default=decimal.Decimal(0.00), max_digits=8, decimal_places=2, help_text='Amount to withdraw from lead payment to be paid to second parent bundler.')
    facebook_chargeback = models.DecimalField(default=CHARGEBACK_PAYMENT, max_digits=8, decimal_places=2, help_text='Chargeback value for Facebook accounts.')
    facebook_screenshot_chargeback = models.DecimalField(default=CHARGEBACK_PAYMENT, max_digits=8, decimal_places=2, help_text='Chargeback value for Facebook Screenshot accounts.')
    google_chargeback = models.DecimalField(default=CHARGEBACK_PAYMENT, max_digits=8, decimal_places=2, help_text='Chargeback value for Google accounts.')
    amazon_chargeback = models.DecimalField(default=CHARGEBACK_PAYMENT, max_digits=8, decimal_places=2, help_text='Chargeback value for AMazon accounts.')
    parent_bundler = models.ForeignKey('adsrental.Bundler', null=True, blank=True, on_delete=models.SET_NULL, help_text='Bundler that gets part of the payment')
    second_parent_bundler = models.ForeignKey('adsrental.Bundler', related_name='second_child_bundler', null=True, blank=True, on_delete=models.SET_NULL, help_text='Second Bundler that gets part of the payment')
    bonus_receiver_bundler = models.ForeignKey('adsrental.Bundler', related_name='bonus_donor', null=True, blank=True, on_delete=models.SET_NULL, help_text='Bundler that receives weekly bonuses for qualified leads.')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @classmethod
    def get_by_utm_source(cls, utm_source: str) -> 'Bundler':
        return cls.objects.filter(utm_source=utm_source).first()

    @classmethod
    def get_by_adsdb_id(cls, adsdb_id: str) -> 'Bundler':
        return cls.objects.filter(adsdb_id=adsdb_id).first()

    def __str__(self) -> str:
        return self.name
        # return '{} ({})'.format(self.name, self.utm_source)
