# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0023_problem_customchecker'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='problem',
            options={'permissions': (('problem_retest', 'Can start a retest'), ('problem_visibility', "Can change problem's visibility"), ('problem_hidden', 'Can see hidden problems')), 'ordering': ['-id']},
        ),
    ]
