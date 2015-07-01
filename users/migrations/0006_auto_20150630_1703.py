# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20150628_1441'),
    ]

    operations = [
        migrations.AlterField(
            model_name='confirmation',
            name='code',
            field=models.CharField(max_length=32, default='E6WDPRQ51FW8FT8JOU120HZ8GR43WY1M'),
        ),
        migrations.AlterField(
            model_name='confirmation',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 30, 14, 3, 54, 199837, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='passreset',
            name='code',
            field=models.CharField(max_length=32, default='I8FQXEGFPJ8SW3I7E49BCV7MGRW209AM'),
        ),
        migrations.AlterField(
            model_name='passreset',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 30, 14, 3, 54, 200487, tzinfo=utc)),
        ),
    ]
