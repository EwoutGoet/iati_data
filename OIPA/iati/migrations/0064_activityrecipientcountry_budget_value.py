# Generated by Django 2.0.13 on 2020-06-30 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0063_renamed_condition_to_conditions'),
    ]

    operations = [
        migrations.AddField(
            model_name='activityrecipientcountry',
            name='budget_value',
            field=models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=255, null=True),
        ),
    ]
