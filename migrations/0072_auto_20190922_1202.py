# pylint: skip-file
# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-09-22 16:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('passive_data_kit', '0071_auto_20190915_1939'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataserver',
            name='source_metadata_url',
            field=models.URLField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='dataserver',
            name='name',
            field=models.CharField(max_length=1024, unique=True),
        ),
        migrations.AlterField(
            model_name='dataserver',
            name='upload_url',
            field=models.URLField(max_length=1024, unique=True),
        ),
    ]
