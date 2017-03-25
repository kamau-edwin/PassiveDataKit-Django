# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-19 21:45
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion

from ..models import install_supports_jsonfield

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('passive_data_kit', '0008_datapointvisualizations'),
    ]
    
    if install_supports_jsonfield():
        operations = [
            migrations.CreateModel(
                name='ReportJob',
                fields=[
                    ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                    ('requested', models.DateTimeField(db_index=True)),
                    ('started', models.DateTimeField(db_index=True)),
                    ('completed', models.DateTimeField(db_index=True)),
                    ('parameters', django.contrib.postgres.fields.jsonb.JSONField()),
                    ('destination', models.EmailField(max_length=1024)),
                    ('report', models.FileField(upload_to='pdk_reports')),
                    ('generator_identifier', models.CharField(db_index=True, max_length=1024)),
                    ('last_updated', models.DateTimeField(db_index=True)),
                    ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ],
            ),
        ]
    else:
        operations = [
            migrations.CreateModel(
                name='ReportJob',
                fields=[
                    ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                    ('requested', models.DateTimeField(db_index=True)),
                    ('started', models.DateTimeField(db_index=True)),
                    ('completed', models.DateTimeField(db_index=True)),
                    ('parameters', models.TextField(max_length=(32 * 1024 * 1024 * 1024))),
                    ('destination', models.EmailField(max_length=1024)),
                    ('report', models.FileField(upload_to='pdk_reports')),
                    ('generator_identifier', models.CharField(db_index=True, max_length=1024)),
                    ('last_updated', models.DateTimeField(db_index=True)),
                    ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ],
            ),
        ]
