
# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-10-27 01:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0057_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activity',
            name='xml_source_ref',
        ),
    ]