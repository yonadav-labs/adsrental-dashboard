# Generated by Django 2.0.3 on 2018-04-04 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adsrental', '0111_readonlylead'),
    ]

    operations = [
        migrations.AddField(
            model_name='leadaccount',
            name='security_checkpoint_date',
            field=models.DateTimeField(blank=True, help_text='Date when security checkpoint has been reported.', null=True),
        ),
    ]