import decimal

from django.db import models

from adsrental.models.bundler_payment import BundlerPayment


class Bundler(models.Model):
    '''
    Stores a single bundler entry, used to get bundler info for lead by *utm_source*
    '''
    PAYMENT = decimal.Decimal(150.00)
    CHARGEBACK_PAYMENT = decimal.Decimal(50.00)
    CHARGEBACK_ROLLING_WINDOW_DAYS = 30
    CHARGEBACK_STREAK = 3

    name = models.CharField(max_length=255, unique=True, db_index=True)
    utm_source = models.CharField(max_length=50, db_index=True, null=True, blank=True)
    url_tag = models.CharField(max_length=50, db_index=True, null=True, blank=True)
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
    facebook_third_parent_payment = models.DecimalField(default=decimal.Decimal(0.00), max_digits=8, decimal_places=2, help_text='Amount to withdraw from lead payment to be paid to third parent bundler.')
    facebook_screenshot_third_parent_payment = models.DecimalField(default=decimal.Decimal(0.00), max_digits=8, decimal_places=2, help_text='Amount to withdraw from lead payment to be paid to parent bundler.')
    google_third_parent_payment = models.DecimalField(default=decimal.Decimal(0.00), max_digits=8, decimal_places=2, help_text='Amount to withdraw from lead payment to be paid to third parent bundler.')
    amazon_third_parent_payment = models.DecimalField(default=decimal.Decimal(0.00), max_digits=8, decimal_places=2, help_text='Amount to withdraw from lead payment to be paid to third parent bundler.')
    facebook_screenshot_chargeback = models.DecimalField(default=CHARGEBACK_PAYMENT, max_digits=8, decimal_places=2, help_text='Chargeback value for Facebook Screenshot accounts.')
    facebook_chargeback = models.DecimalField(default=CHARGEBACK_PAYMENT, max_digits=8, decimal_places=2, help_text='Chargeback value for Facebook accounts.')
    facebook_chargeback_30_days = models.DecimalField(default=CHARGEBACK_PAYMENT, max_digits=8, decimal_places=2, help_text='Chargeback value for Facebook 30+ days active accounts.')
    facebook_chargeback_60_days = models.DecimalField(default=CHARGEBACK_PAYMENT, max_digits=8, decimal_places=2, help_text='Chargeback value for Facebook 60+ days active accounts.')
    facebook_chargeback_90_days = models.DecimalField(default=CHARGEBACK_PAYMENT, max_digits=8, decimal_places=2, help_text='Chargeback value for Facebook 90+ days active accounts.')
    google_chargeback = models.DecimalField(default=CHARGEBACK_PAYMENT, max_digits=8, decimal_places=2, help_text='Chargeback value for Google accounts.')
    google_chargeback_30_days = models.DecimalField(default=CHARGEBACK_PAYMENT, max_digits=8, decimal_places=2, help_text='Chargeback value for Google 30+ days active accounts.')
    google_chargeback_60_days = models.DecimalField(default=CHARGEBACK_PAYMENT, max_digits=8, decimal_places=2, help_text='Chargeback value for Google 60+ days active accounts.')
    google_chargeback_90_days = models.DecimalField(default=CHARGEBACK_PAYMENT, max_digits=8, decimal_places=2, help_text='Chargeback value for Google 90+ days active accounts.')
    amazon_chargeback = models.DecimalField(default=CHARGEBACK_PAYMENT, max_digits=8, decimal_places=2, help_text='Chargeback value for AMazon accounts.')
    amazon_chargeback_30_days = models.DecimalField(default=CHARGEBACK_PAYMENT, max_digits=8, decimal_places=2, help_text='Chargeback value for Amazon 30+ days active accounts.')
    amazon_chargeback_60_days = models.DecimalField(default=CHARGEBACK_PAYMENT, max_digits=8, decimal_places=2, help_text='Chargeback value for Amazon 60+ days active accounts.')
    amazon_chargeback_90_days = models.DecimalField(default=CHARGEBACK_PAYMENT, max_digits=8, decimal_places=2, help_text='Chargeback value for Amazon 90+ days active accounts.')
    chargeback_streak = models.DecimalField(default=CHARGEBACK_STREAK, help_text='How many chargebacks bundler can have in rolling 30 days period.')
    parent_bundler = models.ForeignKey('adsrental.Bundler', null=True, blank=True, on_delete=models.SET_NULL, help_text='Bundler that gets part of the payment')
    second_parent_bundler = models.ForeignKey('adsrental.Bundler', related_name='second_child_bundler', null=True, blank=True, on_delete=models.SET_NULL, help_text='Second Bundler that gets part of the payment')
    third_parent_bundler = models.ForeignKey('adsrental.Bundler', related_name='third_child_bundler', null=True, blank=True, on_delete=models.SET_NULL, help_text='Third Bundler that gets part of the payment')
    bonus_receiver_bundler = models.ForeignKey('adsrental.Bundler', related_name='bonus_donor', null=True, blank=True, on_delete=models.SET_NULL, help_text='Bundler that receives weekly bonuses for qualified leads.')
    team = models.ForeignKey('adsrental.BundlerTeam', related_name='bundlers', null=True, blank=True, on_delete=models.SET_NULL, help_text='Bundler team.')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @classmethod
    def get_by_utm_source(cls, utm_source: str) -> 'Bundler':
        return cls.objects.filter(utm_source=utm_source).first()

    @classmethod
    def get_by_adsdb_id(cls, adsdb_id: str) -> 'Bundler':
        return cls.objects.filter(adsdb_id=adsdb_id).first()

    def is_chargeback_enabled(self, lead_account):
        now = timezone.localtime(timezone.now())
        chargeback_count = BundlerPayment.objects.filter(
            create__gt=now - datetime.timedelta(days=self.CHARGEBACK_ROLLING_WINDOW_DAYS), bundler=self
        ).exclude(lead_account=lead_account).count()
        return chargeback_count <= self.chargeback_streak

    def get_chargeback(self, lead_account) -> decimal.Decimal:
        if not lead_account.charge_back:
            return decimal.Decimal('0.00')

        if not self.is_chargeback_enabled(lead_account):
            return decimal.Decimal('0.00')

        active_days = lead_account.get_active_days()
        if lead_account.account_type in lead_account.ACCOUNT_TYPES_FACEBOOK:
            if active_days >= 90 and self.facebook_chargeback_90_days is not None:
                return self.facebook_chargeback_90_days
            if active_days >= 60 and self.facebook_chargeback_60_days is not None:
                return self.facebook_chargeback_60_days
            if active_days >= 30 and self.facebook_chargeback_30_days is not None:
                return self.facebook_chargeback_30_days
            if self.facebook_chargeback:
                return self.facebook_chargeback
        if lead_account.account_type == lead_account.ACCOUNT_TYPE_GOOGLE:
            if active_days >= 90 and self.google_chargeback_90_days is not None:
                return self.google_chargeback_90_days
            if active_days >= 60 and self.google_chargeback_60_days is not None:
                return self.google_chargeback_60_days
            if active_days >= 30 and self.google_chargeback_30_days is not None:
                return self.google_chargeback_30_days
            if self.google_chargeback:
                return self.google_chargeback
        if lead_account.account_type == lead_account.ACCOUNT_TYPE_AMAZON:
            if active_days >= 90 and self.amazon_chargeback_90_days is not None:
                return self.amazon_chargeback_90_days
            if active_days >= 60 and self.amazon_chargeback_60_days is not None:
                return self.amazon_chargeback_60_days
            if active_days >= 30 and self.amazon_chargeback_30_days is not None:
                return self.amazon_chargeback_30_days
            if self.amazon_chargeback:
                return self.amazon_chargeback

        return decimal.Decimal('0.00')

    def __str__(self) -> str:
        return self.name
        # return '{} ({})'.format(self.name, self.utm_source)
