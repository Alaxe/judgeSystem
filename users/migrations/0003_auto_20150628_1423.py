# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20150628_1254'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userproblemdata',
            name='problem',
        ),
        migrations.RemoveField(
            model_name='userproblemdata',
            name='user',
        ),
        migrations.RemoveField(
            model_name='userstatts',
            name='user',
        ),
        migrations.AlterField(
            model_name='confirmation',
            name='code',
            field=models.CharField(max_length=32, default='1S5YH6W2QZM6M2CAON7SRYVOHW3QGJ6L'),
        ),
        migrations.AlterField(
            model_name='confirmation',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 28, 11, 23, 5, 785908, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='passreset',
            name='code',
            field=models.CharField(max_length=32, default='5OXTRMZ5U464J91IFWXJFTODJSWGI8YW'),
        ),
        migrations.AlterField(
            model_name='passreset',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 28, 11, 23, 5, 786551, tzinfo=utc)),
        ),
        migrations.DeleteModel(
            name='UserProblemData',
        ),
        migrations.DeleteModel(
            name='UserStatts',
        ),
    ]
