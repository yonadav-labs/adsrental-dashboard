import base64

from django import forms
from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget

from adsrental.models.lead import Lead


class DashboardForm(forms.Form):
    EC2_STATE_CHOICES = (
        ('', 'All'),
        ('online', 'Online only'),
        ('offline', 'Offline only'),
        ('offline_2days', 'Offline for last 2 days'),
        ('offline_5days', 'Offline for last 5 days'),
    )
    TUNNEL_STATE_CHOICES = (
        ('', 'All'),
        ('online', 'Online only'),
        ('offline', 'Offline only'),
        ('offline_2days', 'Offline for last 2 days'),
        ('offline_5days', 'Offline for last 5 days'),
    )
    WRONG_PASSWORD_CHOICES = (
        ('', 'All'),
        ('no', 'No'),
        ('yes', 'Yes'),
        ('yes_2days', 'Yes for 2 days'),
        ('yes_5days', 'Yes for 5 days'),
    )
    LEAD_STATUS_CHOICES = (
        ('', 'All'),
        ('Available', 'Available'),
        ('Banned', 'Banned'),
        ('Qualified', 'Qualified'),
        ('In-Progress', 'In-Progress'),
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
    search = forms.CharField(label='Search', required=False)
    lead_status = forms.ChoiceField(label='Lead Status', choices=LEAD_STATUS_CHOICES, required=False)
    ec2_state = forms.ChoiceField(label='EC2 State', choices=EC2_STATE_CHOICES, required=False)
    tunnel_state = forms.ChoiceField(label='Tunnel State', choices=TUNNEL_STATE_CHOICES, required=False)
    wrong_password = forms.ChoiceField(label='Wrong Password', choices=WRONG_PASSWORD_CHOICES, required=False)
    banned = forms.ChoiceField(label='Banned', choices=BANNED_CHOICES, required=False)
    pi_delivered = forms.ChoiceField(label='Delivered', choices=PI_DELIVERED_CHOICES, required=False)
    account_type = forms.ChoiceField(label='Account Type', choices=ACCOUNT_TYPE_CHOICES, required=False)


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

    email = forms.CharField(label='Email', required=True, widget=forms.TextInput(attrs={'size': 40}))
    first_name = forms.CharField(label='First Name', required=True, widget=forms.TextInput(attrs={'size': 40}))
    last_name = forms.CharField(label='Last Name', required=True, widget=forms.TextInput(attrs={'size': 40}))
    phone = forms.CharField(label='Phone', required=True, widget=forms.TextInput(attrs={'size': 40, 'placeholder': '(734) 555-12-12'}))
    facebook_profile_url = forms.CharField(label='Facebook Profile Url', required=True, widget=forms.URLInput(attrs={'size': 40}))
    fb_email = forms.CharField(label='Facebook Email', required=True, widget=forms.TextInput(attrs={'size': 40}))
    fb_secret = forms.CharField(label='Facebook Password', required=True, widget=forms.TextInput(attrs={'size': 40}))
    fb_friends = forms.IntegerField(label='Facebook Friends Count', required=True, widget=forms.NumberInput(attrs={'size': 40}))
    street = forms.CharField(label='Shipping Street', required=True, widget=forms.TextInput(attrs={'size': 40}))
    city = forms.CharField(label='Shipping City', required=True, widget=forms.TextInput(attrs={'size': 40}))
    state = forms.ChoiceField(label='Shipping State', choices=STATE_CHOICES, required=True)
    postal_code = forms.CharField(label='Shipping Zip', required=True, widget=forms.TextInput(attrs={'size': 40}))
    accept = forms.BooleanField(required=True)
    photo_id = forms.FileField(label='Photo ID (JPG, PNG or PDF)', widget=forms.FileInput(attrs={'accept': '.png,.jpg,.pdf'}), required=True)
    captcha = ReCaptchaField(widget=ReCaptchaWidget(), required=False)
    utm_source = forms.CharField(widget=forms.HiddenInput())

    def clean_phone(self):
        value = self.cleaned_data['phone']
        if value.startswith('+1'):
            value = value[2:]

        digits = ''.join([i for i in value if i.isdigit()])
        if len(digits) != 10:
            raise forms.ValidationError("Phone number should have 10 digits excluding +1 code")
        return '({}) {}-{}'.format(value[0:3], value[3:6], value[6:])

    def clean_first_name(self):
        value = self.cleaned_data['first_name'].capitalize()
        return value

    def clean_last_name(self):
        value = self.cleaned_data['last_name'].capitalize()
        return value

    def clean_email(self):
        value = self.cleaned_data['email'].lower()
        existing_valus = [i[0] for i in Lead.objects.all().values_list('email')]
        if value in existing_valus:
            raise forms.ValidationError("This email is already registered")

        return value

    def clean_fb_friends(self):
        value = self.cleaned_data['fb_friends']
        if value == 0:
            raise forms.ValidationError("Incorrect Facebook Friends Count")

        return value

    def clean_facebook_profile_url(self):
        value = self.cleaned_data['facebook_profile_url'].lower()
        existing_valus = [i[0] for i in Lead.objects.all().values_list('fb_profile_url')]
        if value in existing_valus:
            raise forms.ValidationError("This Facebook profile URL is already registered")

        return value

    def clean_fb_email(self):
        value = self.cleaned_data['fb_email'].lower()
        existing_valus = [i[0] for i in Lead.objects.all().values_list('fb_email')]
        if base64.b64encode(value) in existing_valus:
            raise forms.ValidationError("This Facebook email is already registered")

        return value


class ReportForm(forms.Form):
    MONTH_CURRENT = '2018-01'
    MONTH_CHOICES = (
        (MONTH_CURRENT, 'Jan 2018', ),
        ('2018-02', 'Feb 2018', ),
    )

    search = forms.CharField(label='Search', required=False)
    month = forms.ChoiceField(choices=MONTH_CHOICES, required=False)
