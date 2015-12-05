# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import media_manager.models


class Migration(migrations.Migration):

    dependencies = [
        ('media_manager', '0002_auto_20151205_0840'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mediafile',
            name='media',
            field=models.FileField(upload_to=media_manager.models.get_mediafile_loc),
        ),
    ]
