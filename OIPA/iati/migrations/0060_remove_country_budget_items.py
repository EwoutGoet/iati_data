
# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-12-08 15:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0059_auto_20161121_1613'),
    ]

    def remove_all_wopa(apps, schema_editor):
        try: # don't run on first migration
            CountryBudgetItem = apps.get_model('iati', 'CountryBudgetItem')
        except:
            return

        CountryBudgetItem.objects.all().delete()


    operations = [
        migrations.RunPython(remove_all_wopa, lambda x,y: None),
    ]
