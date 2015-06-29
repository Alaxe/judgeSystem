# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0005_auto_20150624_1800'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='maxScore',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='solution',
            name='score',
            field=models.IntegerField(default=0),
        ),
    ]
