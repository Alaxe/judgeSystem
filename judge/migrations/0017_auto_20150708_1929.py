# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0016_auto_20150706_1737'),
    ]

    operations = [
        migrations.RenameField(
            model_name='test',
            old_name='points',
            new_name='score',
        ),
    ]
