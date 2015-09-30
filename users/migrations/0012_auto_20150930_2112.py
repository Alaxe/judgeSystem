# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_auto_20150930_2050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='confirmation',
            name='code',
            field=models.CharField(max_length=32, default='SZ6lmNwKUvlv'),
        ),
        migrations.AlterField(
            model_name='passreset',
            name='code',
            field=models.CharField(max_length=32, default='ZfBVNHLZQKpf'),
        ),
    ]
