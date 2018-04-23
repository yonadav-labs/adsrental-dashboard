# Generated by Django 2.0.3 on 2018-04-20 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adsrental', '0122_auto_20180418_1137'),
    ]

    operations = [
        migrations.CreateModel(
            name='BundlerPaymentsReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_index=True, unique=True)),
                ('pdf', models.FileField(upload_to='')),
                ('html', models.TextField()),
            ],
        ),
    ]