# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-09 18:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adsrental', '0090_auto_20180309_0911'),
    ]

    operations = [
        migrations.AddField(
            model_name='raspberrypi',
            name='ip_address',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
