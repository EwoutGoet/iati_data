# Generated by Django 2.0.6 on 2019-02-21 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iati_synchroniser', '0011_dataset_internal_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='internal_url',
            field=models.URLField(blank=True, max_length=255),
        ),
    ]
