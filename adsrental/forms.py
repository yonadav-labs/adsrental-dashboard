from django import forms
from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget


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

    email = forms.CharField(required=True, widget=forms.TextInput(attrs={'size': 40}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'size': 40}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'size': 40}))
    phone = forms.CharField(required=True, widget=forms.TextInput(attrs={'size': 40}))
    facebook_profile_url = forms.CharField(required=True, widget=forms.URLInput(attrs={'size': 40}))
    fb_email = forms.CharField(required=True, widget=forms.TextInput(attrs={'size': 40}))
    fb_secret = forms.CharField(required=True, widget=forms.TextInput(attrs={'size': 40}))
    fb_friends = forms.IntegerField(required=True, widget=forms.NumberInput(attrs={'size': 40}))
    street = forms.CharField(required=True, widget=forms.TextInput(attrs={'size': 40}))
    city = forms.CharField(required=True, widget=forms.TextInput(attrs={'size': 40}))
    state = forms.ChoiceField(choices=STATE_CHOICES, required=True)
    postal_code = forms.CharField(required=True, widget=forms.TextInput(attrs={'size': 40}))
    registered_isp = forms.CharField(required=False)
    accept = forms.BooleanField(required=True)
    photo_id = forms.FileField(widget=forms.FileInput(attrs={'accept': '.png,.jpg,.pdf'}), required=True)
    captcha = ReCaptchaField(widget=ReCaptchaWidget())
    utm_source = forms.CharField(widget=forms.HiddenInput())


class ReportForm(forms.Form):
    MONTH_CURRENT = '2018-01'
    MONTH_CHOICES = (
        (MONTH_CURRENT, 'Jan 2018', ),
        ('2018-02', 'Feb 2018', ),
    )
    month = forms.ChoiceField(choices=MONTH_CHOICES)
