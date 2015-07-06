# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20150630_1703'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userstatts',
            name='user',
        ),
        migrations.AlterField(
            model_name='confirmation',
            name='code',
            field=models.CharField(max_length=32, default='85DQHD6EXONHC96AK2MBUEV1AWAMJVMM'),
        ),
        migrations.AlterField(
            model_name='confirmation',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 4, 15, 59, 45, 856579, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='passreset',
            name='code',
            field=models.CharField(max_length=32, default='GY8WIRBEMWCKFIE0NF87P41R23IH458X'),
        ),
        migrations.AlterField(
            model_name='passreset',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 4, 15, 59, 45, 857234, tzinfo=utc)),
        ),
        migrations.DeleteModel(
            name='UserStatts',
        ),
    ]
