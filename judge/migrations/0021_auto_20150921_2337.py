# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0020_problem_tags'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='problem',
            options={'ordering': ['-id'], 'permissions': (('problem_retest', 'Can start a retest'), ('problem_visibility', "Can change problem's visibility"))},
        ),
    ]
