# Generated by Django 2.0.13 on 2020-10-09 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('currency_convert', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='monthlyaverage',
            name='imf_url',
            field=models.URLField(max_length=2000, null=True),
        ),
    ]
