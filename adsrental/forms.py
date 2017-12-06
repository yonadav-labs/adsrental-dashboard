from django import forms


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
    ec2_state = forms.ChoiceField(label='EC2 state', choices=EC2_STATE_CHOICES, required=False)
    tunnel_state = forms.ChoiceField(label='Tunnel state', choices=TUNNEL_STATE_CHOICES, required=False)
    wrong_password = forms.ChoiceField(label='Wrong Password', choices=WRONG_PASSWORD_CHOICES, required=False)
