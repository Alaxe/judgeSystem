# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20150628_1440'),
    ]

    operations = [
        migrations.AlterField(
            model_name='confirmation',
            name='code',
            field=models.CharField(max_length=32, default='2XB90101RNZLYK3YFARNA38ZJHY2UFMA'),
        ),
        migrations.AlterField(
            model_name='confirmation',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 28, 11, 41, 4, 700906, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='passreset',
            name='code',
            field=models.CharField(max_length=32, default='52KUATDLBEKPVL2DMK9RFDQ6HDEEBV65'),
        ),
        migrations.AlterField(
            model_name='passreset',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 28, 11, 41, 4, 701544, tzinfo=utc)),
        ),
    ]
