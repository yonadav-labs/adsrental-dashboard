import re

from django import forms
from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget

from adsrental.models.lead import Lead
from adsrental.models.lead_account import LeadAccount


class DashboardForm(forms.Form):
    RASPBERRY_PI_STATUS_CHOICES = (
        ('', 'All'),
        ('online', 'Online only'),
        ('offline', 'Offline only'),
        ('offline_0_2days', 'Offline for last 0-2 days'),
        ('offline_3_5days', 'Offline for last 3-5  days'),
        ('offline_5days', 'Offline for more than 5 days'),
        ('never', 'Never'),
    )
    WRONG_PASSWORD_CHOICES = (
        ('', 'All'),
        ('no', 'No'),
        ('yes', 'Yes'),
        ('yes_0_2days', 'Wrong for 0-2 days'),
        ('yes_3_5days', 'Wrong for 3-5 days'),
        ('yes_5days', 'Wrong for more than 5 days'),
    )
    SECURITY_CHECKPOINT_CHOICES = (
        ('', 'All'),
        ('no', 'No'),
        ('yes', 'Reported'),
        ('yes_0_2days', 'Reported for 0-2 days'),
        ('yes_3_5days', 'Reported for 3-5 days'),
        ('yes_5days', 'Reported for more than 5 days'),
    )
    LEAD_STATUS_CHOICES = (
        ('', 'All'),
        (Lead.STATUS_AVAILABLE, 'Available'),
        (Lead.STATUS_BANNED, 'Banned'),
        (Lead.STATUS_QUALIFIED, 'Qualified'),
        (Lead.STATUS_DISQUALIFIED, 'Disualified'),
        (Lead.STATUS_IN_PROGRESS, 'In-Progress'),
    )
    BANNED_CHOICES = (
        ('', 'All'),
        ('true', 'Banned', ),
        ('false', 'Not banned', ),
    )
    PI_DELIVERED_CHOICES = (
        ('', 'All'),
        ('true', 'Yes', ),
        ('false', 'No', ),
    )
    ACCOUNT_TYPE_CHOICES = (
        ('', 'All'),
        ('facebook', 'Facebook', ),
        ('google', 'Google', ),
    )
    SHIPSTATION_ORDER_STATUS_CHOICES = (
        ('', 'All'),
        ('shipped', 'Shipped', ),
        ('awaiting_shipment', 'Awaiting', ),
        ('on_hold', 'On Hold', ),
        ('cancelled', 'Cancelled', ),
    )
    search = forms.CharField(label='Search', required=False)
    lead_status = forms.ChoiceField(label='Status', choices=LEAD_STATUS_CHOICES, required=False)
    raspberry_pi_status = forms.ChoiceField(label='RaspberryPi Online state', choices=RASPBERRY_PI_STATUS_CHOICES, required=False)
    wrong_password = forms.ChoiceField(label='Wrong Password', choices=WRONG_PASSWORD_CHOICES, required=False)
    security_checkpoint = forms.ChoiceField(label='Security Checkpoint', choices=SECURITY_CHECKPOINT_CHOICES, required=False)
    banned = forms.ChoiceField(label='Banned', choices=BANNED_CHOICES, required=False)
    pi_delivered = forms.ChoiceField(label='Delivered', choices=PI_DELIVERED_CHOICES, required=False)
    account_type = forms.ChoiceField(label='Account Type', choices=ACCOUNT_TYPE_CHOICES, required=False)
    shipstation_order_status = forms.ChoiceField(label='Order status', choices=SHIPSTATION_ORDER_STATUS_CHOICES, required=False)


class SetPasswordForm(forms.Form):
    lead_email = forms.CharField(label='Lead Email', widget=forms.TextInput(attrs={'readonly': True}))
    email = forms.CharField(label='Email', widget=forms.TextInput(attrs={'readonly': True}))
    new_password = forms.CharField(label='Password')

    def update_lead_account(self, lead_account):
        lead_account.password = self.cleaned_data['new_password']
        lead_account.wrong_password_date = None
        lead_account.save()


class ChangeAddressForm(forms.Form):
    street = forms.CharField(label='Street')
    city = forms.CharField(label='City')
    country = forms.CharField(label='Country', widget=forms.TextInput(attrs={'readonly': True}), required=False)
    state = forms.CharField(label='State')
    postal_code = forms.CharField(label='Postal code')

    def update_lead(self, lead):
        lead.street = self.cleaned_data['street']
        lead.city = self.cleaned_data['city']
        lead.state = self.cleaned_data['state']
        lead.postal_code = self.cleaned_data['postal_code']
        lead.save()


class SignupForm(forms.Form):
    STATE_CHOICES = (
        ('Alabama', 'Alabama', ),
        ('Alaska', 'Alaska', ),
        ('Arizona', 'Arizona', ),
        ('Arkansas', 'Arkansas', ),
        ('California', 'California', ),
        ('Colorado', 'Colorado', ),
        ('Connecticut', 'Connecticut', ),
        ('Delaware', 'Delaware', ),
        ('Florida', 'Florida', ),
        ('Georgia', 'Georgia', ),
        ('Hawaii', 'Hawaii', ),
        ('Idaho', 'Idaho', ),
        ('Illinois', 'Illinois', ),
        ('Indiana', 'Indiana', ),
        ('Iowa', 'Iowa', ),
        ('Kansas', 'Kansas', ),
        ('Kentucky', 'Kentucky', ),
        ('Louisiana', 'Louisiana', ),
        ('Maine', 'Maine', ),
        ('Maryland', 'Maryland', ),
        ('Massachusetts', 'Massachusetts', ),
        ('Michigan', 'Michigan', ),
        ('Minnesota', 'Minnesota', ),
        ('Mississippi', 'Mississippi', ),
        ('Missouri', 'Missouri', ),
        ('Montana', 'Montana', ),
        ('Nebraska', 'Nebraska', ),
        ('Nevada', 'Nevada', ),
        ('New Hampshire', 'New Hampshire', ),
        ('New Jersey', 'New Jersey', ),
        ('New Mexico', 'New Mexico', ),
        ('New York', 'New York', ),
        ('North Carolina', 'North Carolina', ),
        ('North Dakota', 'North Dakota', ),
        ('Ohio', 'Ohio', ),
        ('Oklahoma', 'Oklahoma', ),
        ('Oregon', 'Oregon', ),
        ('Pennsylvania', 'Pennsylvania', ),
        ('Rhode Island', 'Rhode Island', ),
        ('South Carolina', 'South Carolina', ),
        ('South Dakota', 'South Dakota', ),
        ('Tennessee', 'Tennessee', ),
        ('Texas', 'Texas', ),
        ('Utah', 'Utah', ),
        ('Vermont', 'Vermont', ),
        ('Virginia', 'Virginia', ),
        ('Washington', 'Washington', ),
        ('West Virginia', 'West Virginia', ),
        ('Wisconsin', 'Wisconsin', ),
        ('Wyoming', 'Wyoming', ),
    )
    APPLY_TYPE_SPLASHTOP = 'splashtop'
    APPLY_TYPE_SCREENSHOT = 'screenshot'

    email = forms.CharField(label='Email', required=True, widget=forms.TextInput(attrs={'size': 40}))
    first_name = forms.CharField(label='First Name', required=True, widget=forms.TextInput(attrs={'size': 40}))
    last_name = forms.CharField(label='Last Name', required=True, widget=forms.TextInput(attrs={'size': 40}))
    phone = forms.CharField(label='Phone', required=True, widget=forms.TextInput(attrs={'size': 40, 'placeholder': '(XXX) XXX-XXXX'}))
    facebook_profile_url = forms.CharField(label='Facebook Profile Url', required=True, widget=forms.URLInput(attrs={'size': 40}))
    fb_email = forms.CharField(label='Facebook Email', required=True, widget=forms.TextInput(attrs={'size': 40}))
    fb_secret = forms.CharField(label='Facebook Password', required=True, widget=forms.TextInput(attrs={'size': 40}))
    fb_friends = forms.IntegerField(label='Facebook Friends Count', required=True, widget=forms.NumberInput(attrs={'size': 40}))
    street = forms.CharField(label='Shipping Street', required=True, widget=forms.TextInput(attrs={'size': 40}))
    city = forms.CharField(label='Shipping City', required=True, widget=forms.TextInput(attrs={'size': 40}))
    state = forms.ChoiceField(label='Shipping State', choices=STATE_CHOICES, required=True)
    postal_code = forms.CharField(label='Shipping Zip', required=True, widget=forms.TextInput(attrs={'size': 40}))
    accept = forms.BooleanField(required=True)
    age_check = forms.BooleanField(label='I am at least 18 years old', required=True)
    photo_id = forms.FileField(label='Photo ID (JPG, PNG or PDF)', widget=forms.FileInput(attrs={'accept': '.png,.jpg,.pdf'}), required=True)
    extra_photo_id = forms.FileField(label='Second Photo ID (JPG, PNG or PDF)', widget=forms.FileInput(attrs={'accept': '.png,.jpg,.pdf'}), required=False)
    captcha = ReCaptchaField(widget=ReCaptchaWidget(), required=False)
    apply_type = forms.RadioSelect(choices=(
        (APPLY_TYPE_SPLASHTOP, 'Apply with Splashtop (Recommended) - This is our quickest and easiest way to get qualified', ),
        (APPLY_TYPE_SCREENSHOT, 'Apply with Screenshots (More time consuming) - This method is only for people who have a router but do not own a computer. This method is more time consuming, pay is lower and you will be required to provide additional documentation.', ),
    ))
    utm_source = forms.CharField(widget=forms.HiddenInput())

    def clean_phone(self):
        value = self.cleaned_data['phone']
        if value.startswith('+1'):
            value = value[2:]

        digits = ''.join([i for i in value if i.isdigit()])
        if len(digits) != 10:
            raise forms.ValidationError("Phone number should have 10 digits excluding +1 code")

        lead = Lead.objects.filter(phone=digits).first()
        if lead:
            raise forms.ValidationError("This phone number is already registered")
        return digits

    def clean_first_name(self):
        value = self.cleaned_data['first_name'].title()
        return value

    def clean_last_name(self):
        value = self.cleaned_data['last_name'].title()
        return value

    def clean_email(self):
        value = self.cleaned_data['email'].lower()
        lead = Lead.objects.filter(email=value).first()
        if lead:
            raise forms.ValidationError("This email is already registered")

        return value

    def clean_fb_friends(self):
        value = self.cleaned_data['fb_friends']
        if value == 0:
            raise forms.ValidationError("Incorrect Facebook Friends Count")

        return value

    def clean_facebook_profile_url(self):
        value = self.cleaned_data['facebook_profile_url'].lower()
        lead_account = LeadAccount.objects.filter(url=value, active=True).first()
        if lead_account:
            raise forms.ValidationError("This Facebook profile URL is already registered")

        return value

    def clean_fb_email(self):
        value = self.cleaned_data['fb_email'].lower()
        lead_account = LeadAccount.objects.filter(username=value, active=True).first()
        if lead_account:
            raise forms.ValidationError("This Facebook email is already registered")

        return value


class ReportForm(forms.Form):
    MONTH_CURRENT = '2018-02'
    MONTH_CHOICES = (
        ('2018-01', 'Jan 2018', ),
        ('2018-02', 'Feb 2018', ),
    )
    AMOUNT_CHOICES = (
        ('', 'All', ),
        ('0.01', 'More than $0', ),
        ('2', 'More than $2', ),
    )

    search = forms.CharField(label='Search', required=False)
    month = forms.ChoiceField(choices=MONTH_CHOICES, required=False)
    amount = forms.ChoiceField(choices=AMOUNT_CHOICES, required=False)

    def clean_month(self):
        value = self.cleaned_data['month'].lower()
        if not value:
            return self.MONTH_CURRENT

        return value


class LandingForm(forms.Form):
    email = forms.CharField(label='Email', required=True, widget=forms.TextInput(attrs={'placeholder': 'Email', 'class': 'email', }))
    first_name = forms.CharField(label='First Name', required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'name', }))
    last_name = forms.CharField(label='Last Name', required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'name', }))
    age_check = forms.BooleanField(label='I am at least 18 years old', widget=forms.CheckboxInput(attrs={'class': 'age_checkbox', }), required=True)


class AdminLeadAccountBanForm(forms.Form):
    reason = forms.ChoiceField(choices=LeadAccount.BAN_REASON_CHOICES)


class AdminLeadDeleteForm(forms.Form):
    CHECK_CORRECT = 'DELETE'

    check = forms.CharField(label='Password')

    def clean_check(self):
        value = self.cleaned_data['check']
        if value != self.CHECK_CORRECT:
            raise forms.ValidationError("Invalid password, you cannot delete leads")

        return value

class AdminLeadAccountPasswordForm(forms.Form):
    old_password = forms.CharField(label='Old password', widget=forms.TextInput(attrs=dict(readonly=True)), required=False)
    new_password = forms.CharField(label='New password')


class AdminPrepareForReshipmentForm(forms.Form):
    rpids = forms.CharField(widget=forms.Textarea())

    def clean_rpids(self):
        value = self.cleaned_data['rpids']
        return re.findall(r'RP\d+', value)


class UserLoginForm(forms.Form):
    first_name = forms.CharField(label='First name', required=True)
    last_name = forms.CharField(label='Last name', required=True)
    postal_code = forms.CharField(label='Zip code', required=True)

    def get_lead(self, data):
        leads = Lead.objects.filter(
            first_name__iexact=data.get('first_name'),
            last_name__iexact=data.get('last_name'),
            postal_code=data.get('postal_code'),
        ).order_by('-created')

        if not leads:
            return None

        for lead in leads:
            if lead.is_active():
                return lead

        first_lead = leads.first()
        return first_lead


    def clean(self):
        cleaned_data = super().clean()

        lead = self.get_lead(cleaned_data)

        if not lead:
            self.add_error('first_name', 'User not found')


class UserFixPasswordForm(forms.Form):
    lead_account_id = forms.CharField(widget=forms.HiddenInput())
    new_password = forms.CharField(label='New password', required=True)

    def get_lead_account(self, data, lead):
        return LeadAccount.objects.filter(
            id=data.get('lead_account_id'),
            lead=lead,
        ).first()

class DisqualifyLeadAccountForm(forms.Form):
    ACTION_SUBMIT = 'submit'

    next = forms.CharField(widget=forms.HiddenInput())
    action = forms.CharField(widget=forms.HiddenInput())

    def clean_action(self):
        value = self.cleaned_data['action']
        if value != self.ACTION_SUBMIT:
            raise forms.ValidationError("Submit cancelled")
