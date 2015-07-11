# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0002_auto_20150709_1924'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='label',
            field=models.CharField(max_length=32, unique=True, verbose_name='Tag'),
        ),
    ]
