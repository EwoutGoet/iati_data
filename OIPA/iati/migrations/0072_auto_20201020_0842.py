# Generated by Django 2.0.13 on 2020-10-20 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0071_auto_20200904_0706'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='imf_url',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='usd_exchange_rate',
            field=models.DecimalField(decimal_places=10, max_digits=15, null=True),
        ),
    ]