# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-06 11:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iati_synchroniser', '0007_auto_20170621_0049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='last_found_in_registry',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
