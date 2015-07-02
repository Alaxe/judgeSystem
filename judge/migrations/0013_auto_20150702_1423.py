# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0012_auto_20150702_1410'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='solution',
            name='exec_time',
        ),
        migrations.AddField(
            model_name='testresult',
            name='exec_time',
            field=models.CharField(default='N\\A', max_length=16),
            preserve_default=False,
        ),
    ]
