# pylint: skip-file
# pylint: skip-file
# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-05 23:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('passive_data_kit', '0050_datasourcereference'),
    ]

    operations = [
        migrations.AddField(
            model_name='datapoint',
            name='source_reference',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='data_points', to='passive_data_kit.DataSourceReference'),
        ),
    ]
