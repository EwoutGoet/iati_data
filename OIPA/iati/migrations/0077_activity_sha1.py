# Generated by Django 2.0.13 on 2021-01-15 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0076_auto_20201106_1302'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='sha1',
            field=models.CharField(blank=True, default='', max_length=40),
        ),
    ]
