# Generated by Django 2.1.7 on 2019-05-01 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adsrental', '0245_leadaccount_disable_auto_ban_until'),
    ]

    operations = [
        migrations.AddField(
            model_name='bundler',
            name='url_tag',
            field=models.CharField(blank=True, db_index=True, max_length=50, null=True),
        ),
    ]
