# Generated by Django 2.0.13 on 2019-08-26 14:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati_organisation', '0003_documentlinkdescription'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='organisation',
            options={'ordering': ['organisation_identifier']},
        ),
    ]
