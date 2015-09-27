# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0022_auto_20150926_1759'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='customChecker',
            field=models.BooleanField(default=False),
        ),
    ]
