# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0004_auto_20150524_1633'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='confirmation',
            name='user',
        ),
        migrations.DeleteModel(
            name='Confirmation',
        ),
        migrations.RemoveField(
            model_name='passreset',
            name='user',
        ),
        migrations.DeleteModel(
            name='PassReset',
        ),
        migrations.AlterModelOptions(
            name='problem',
            options={'ordering': ['-id']},
        ),
    ]
