# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0007_userproblemdata_userstatts'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userstatts',
            name='user',
        ),
        migrations.DeleteModel(
            name='UserStatts',
        ),
    ]
