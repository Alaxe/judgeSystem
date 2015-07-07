# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20150707_2127'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='blogpost',
            options={'permissions': (('edit_foreign_post', "Edit someone else's post"),), 'ordering': ('-post_time',)},
        ),
    ]
