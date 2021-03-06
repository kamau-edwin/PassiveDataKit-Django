# pylint: skip-file
# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-08-05 20:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('passive_data_kit', '0061_databundle_compression'),
    ]

    operations = [
        migrations.AlterField(
            model_name='databundle',
            name='compression',
            field=models.CharField(choices=[('none', 'None'), ('gzip', 'GZip')], db_index=True, default='none', max_length=128),
        ),
    ]
