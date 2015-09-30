# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20150930_2112'),
    ]

    operations = [
        migrations.AlterField(
            model_name='confirmation',
            name='code',
            field=models.CharField(max_length=32, default='ER5CHTEJL58838ACYTJLHUP2EWEZ1H1A'),
        ),
        migrations.AlterField(
            model_name='passreset',
            name='code',
            field=models.CharField(max_length=32, default='NW5W4172J2XK6MYPQJR6PDELCHQEF62G'),
        ),
    ]
