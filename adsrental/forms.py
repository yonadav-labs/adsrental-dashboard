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
    LEAD_STATUS_CHOICES = (
        ('', 'All'),
        ('Available', 'Available'),
        ('Banned', 'Banned'),
        ('Qualified', 'Qualified'),
        ('In-Progress', 'In-Progress'),
    )
    lead_status = forms.ChoiceField(label='Lead Status', choices=LEAD_STATUS_CHOICES, required=False)
    ec2_state = forms.ChoiceField(label='EC2 State', choices=EC2_STATE_CHOICES, required=False)
    tunnel_state = forms.ChoiceField(label='Tunnel State', choices=TUNNEL_STATE_CHOICES, required=False)
    wrong_password = forms.ChoiceField(label='Wrong Password', choices=WRONG_PASSWORD_CHOICES, required=False)
