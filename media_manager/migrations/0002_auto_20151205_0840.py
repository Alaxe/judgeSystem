# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media_manager', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mediafile',
            old_name='mediae',
            new_name='media',
        ),
    ]
