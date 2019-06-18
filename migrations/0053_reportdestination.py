# pylint: skip-file
# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-17 19:57
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion

from ..models import install_supports_jsonfield

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('passive_data_kit', '0052_auto_20190408_0724'),
    ]

    if install_supports_jsonfield():
		operations = [
			migrations.CreateModel(
				name='ReportDestination',
				fields=[
					('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
					('destination', models.CharField(max_length=4096)),
					('description', models.CharField(blank=True, max_length=4096, null=True)),
					('parameters', django.contrib.postgres.fields.jsonb.JSONField()),
					('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pdk_report_destinations', to=settings.AUTH_USER_MODEL)),
				],
			),
		]
    else:
		operations = [
			migrations.CreateModel(
				name='ReportDestination',
				fields=[
					('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
					('destination', models.CharField(max_length=4096)),
					('description', models.CharField(blank=True, max_length=4096, null=True)),
					('parameters', models.TextField(max_length=(32 * 1024 * 1024 * 1024))),
					('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pdk_report_destinations', to=settings.AUTH_USER_MODEL)),
				],
			),
		]
