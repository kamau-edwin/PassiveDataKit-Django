# pylint: skip-file
# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-11-15 21:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('passive_data_kit', '0076_deviceissue_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='deviceissue',
            name='device_model',
            field=models.CharField(blank=True, max_length=1048576, null=True),
        ),
    ]
