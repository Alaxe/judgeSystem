# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0010_auto_20150702_1223'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='solution',
            options={'permissions': (('view_foreign_solution', "Can see somebody else's solution"),), 'ordering': ['-submit_date']},
        ),
    ]
