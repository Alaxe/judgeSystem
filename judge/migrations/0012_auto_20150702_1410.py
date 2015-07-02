# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0011_auto_20150702_1248'),
    ]

    operations = [
        migrations.AddField(
            model_name='solution',
            name='exec_time',
            field=models.CharField(default='N/A', max_length=16),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='solution',
            name='grader_message',
            field=models.CharField(max_length=32),
        ),
    ]
