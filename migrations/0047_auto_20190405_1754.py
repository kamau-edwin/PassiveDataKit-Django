# pylint: skip-file
# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-05 21:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('passive_data_kit', '0046_merge_20190330_2353'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataGeneratorDefinition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('generator_identifier', models.CharField(max_length=1024)),
                ('name', models.CharField(max_length=1024)),
                ('description', models.TextField(blank=True, max_length=1048576, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='datapoint',
            name='generator_definition',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='passive_data_kit.DataGeneratorDefinition'),
        ),
    ]
