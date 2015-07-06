# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0015_problem_public'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='problem',
            options={'permissions': (('retest_problem', 'Can start a retest'), ('prbolem_visibility', 'Can change problem visibility')), 'ordering': ['-id']},
        ),
        migrations.RenameField(
            model_name='problem',
            old_name='public',
            new_name='visible',
        ),
    ]
