# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20150929_2142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='confirmation',
            name='code',
            field=models.CharField(default='JUDYHCY379K52XHPY4FN6879NHV9CGZE', max_length=32),
        ),
        migrations.AlterField(
            model_name='passreset',
            name='code',
            field=models.CharField(default='X1GUZNFWY7VNJ7LU355TTBU9IOU00S9A', max_length=32),
        ),
    ]
