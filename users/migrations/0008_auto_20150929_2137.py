# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20150704_1859'),
    ]

    operations = [
        migrations.AlterField(
            model_name='confirmation',
            name='code',
            field=models.CharField(max_length=32, default='ESY85B2XMSJ569XMXL1DHZJXA9GCNVRU'),
        ),
        migrations.AlterField(
            model_name='confirmation',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='passreset',
            name='code',
            field=models.CharField(max_length=32, default='M9TWENK8WVV9HYJF05R5C9VXCSZW7X9U'),
        ),
        migrations.AlterField(
            model_name='passreset',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
