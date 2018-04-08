# Generated by Django 2.0.3 on 2018-04-08 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adsrental', '0117_auto_20180406_1245'),
    ]

    operations = [
        migrations.AddField(
            model_name='leadaccount',
            name='last_security_checkpoint_reported',
            field=models.DateTimeField(blank=True, help_text='Date when security checkpoint notification was sent.', null=True),
        ),
    ]
