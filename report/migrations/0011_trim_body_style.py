# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-08-02 07:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0010_auto_20160708_1614'),
    ]

    operations = [
        migrations.AddField(
            model_name='trim',
            name='body_style',
            field=models.CharField(blank=True, default='', max_length=128),
        ),
    ]