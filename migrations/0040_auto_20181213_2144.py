# pylint: skip-file

# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-12-13 21:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('passive_data_kit', '0039_dataservermetadatum_last_updated'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dataservermetadatum',
            options={'verbose_name_plural': 'data server metadata'},
        ),
        migrations.AddField(
            model_name='reportjob',
            name='data_end',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='reportjob',
            name='data_start',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
