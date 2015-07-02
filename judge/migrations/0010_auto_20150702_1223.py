# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0009_userproblemdata_last_submit'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='problem',
            options={'permissions': (('retest_problem', 'Can start a retest'),), 'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='test',
            options={'permissions': (('view_test', 'Can see input/output files'),)},
        ),
    ]
