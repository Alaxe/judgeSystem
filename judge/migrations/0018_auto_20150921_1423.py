# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0017_auto_20150708_1929'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='problem',
            options={'permissions': (('retest_problem', 'Can start a retest'), ('problem_visibility', "Can change problem's visibility"), ('edit_tags', "Can change problem's tags")), 'ordering': ['-id']},
        ),
    ]
