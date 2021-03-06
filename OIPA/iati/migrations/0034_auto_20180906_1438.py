# Generated by Django 2.0.6 on 2018-09-06 14:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0033_auto_20180831_1044'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResultIndicatorPeriodActual',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(blank=True, default='', max_length=50)),
            ],
        ),
        migrations.RemoveField(
            model_name='resultindicatorperiod',
            name='actual',
        ),
        migrations.AddField(
            model_name='resultindicatorperiodactual',
            name='result_indicator_period',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='actuals', to='iati.ResultIndicatorPeriod'),
        ),
    ]
