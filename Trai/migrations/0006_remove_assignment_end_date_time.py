# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-04-29 05:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Trai', '0005_auto_20170427_1322'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assignment',
            name='end_date_time',
        ),
    ]