# pylint: skip-file
# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-11-15 21:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('passive_data_kit', '0074_auto_20191030_0902'),
    ]

    operations = [
        migrations.AddField(
            model_name='deviceissue',
            name='app',
            field=models.CharField(blank=True, max_length=1048576, null=True),
        ),
        migrations.AddField(
            model_name='deviceissue',
            name='correctness_related',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='deviceissue',
            name='version',
            field=models.CharField(blank=True, max_length=1048576, null=True),
        ),
    ]
