# Generated by Django 2.0.6 on 2018-06-25 23:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adsrental', '0170_auto_20180623_1216'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='extra_photo_id',
            field=models.FileField(blank=True, help_text='Extra photo uploaded by user on registration.', null=True, upload_to=''),
        ),
    ]