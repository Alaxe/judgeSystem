# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_auto_20150930_2119'),
    ]

    operations = [
        migrations.AlterField(
            model_name='confirmation',
            name='code',
            field=models.CharField(max_length=32, default=''),
        ),
        migrations.AlterField(
            model_name='passreset',
            name='code',
            field=models.CharField(max_length=32, default=''),
        ),
    ]
