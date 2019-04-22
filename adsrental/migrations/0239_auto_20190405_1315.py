# Generated by Django 2.1.7 on 2019-04-05 20:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adsrental', '0238_auto_20190403_1103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='raspberrypi',
            name='proxy_hostname',
            field=models.CharField(choices=[('178.128.1.68', 'Proxykeeper'), ('138.197.219.240', 'Proxykeeper2'), ('138.197.197.65', 'Proxykeeper3')], default='178.128.1.68', help_text='Hostname tunnel to proxykeeper', max_length=50),
        ),
    ]