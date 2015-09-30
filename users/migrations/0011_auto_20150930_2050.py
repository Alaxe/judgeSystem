# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_auto_20150929_2143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='confirmation',
            name='code',
            field=models.CharField(max_length=32, default='HTJ47ED8KYYYY2RPTTJ5NAZVYC6XBBGQ'),
        ),
        migrations.AlterField(
            model_name='passreset',
            name='code',
            field=models.CharField(max_length=32, default='1RBTXITO4T8R2TNSDDK4EDH2X7AGYXHF'),
        ),
    ]
