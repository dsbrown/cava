# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-06-30 19:25
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0005_auto_20160630_1924'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='modelalias',
            name='trim',
        ),
    ]
