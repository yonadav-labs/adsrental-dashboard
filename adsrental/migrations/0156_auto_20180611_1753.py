# Generated by Django 2.0.5 on 2018-06-12 00:53

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('adsrental', '0155_auto_20180611_1355'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leadaccount',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
