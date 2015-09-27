# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0021_auto_20150921_2337'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='test',
            options={'ordering': ['pk'], 'permissions': (('view_test', 'Can see input/output files'),)},
        ),
    ]
