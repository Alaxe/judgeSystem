# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-10 18:18
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0035_auto_20151210_1936'),
    ]

    operations = [
        migrations.RenameField(
            model_name='problem',
            old_name='maxScore',
            new_name='max_score',
        ),
    ]
