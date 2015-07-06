# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0014_userstatts'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='public',
            field=models.BooleanField(default=False),
        ),
    ]
