# pylint: skip-file
# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-09 15:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('passive_data_kit', '0056_auto_20190520_0028'),
    ]

    operations = [
        migrations.AddField(
            model_name='databundle',
            name='encrypted',
            field=models.BooleanField(default=False),
        ),
    ]
