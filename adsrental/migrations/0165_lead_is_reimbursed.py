# Generated by Django 2.0.6 on 2018-06-20 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adsrental', '0164_auto_20180618_0926'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='is_reimbursed',
            field=models.BooleanField(default=False, help_text='Lead is active for more than 5 months and gets pay checks.'),
        ),
    ]
