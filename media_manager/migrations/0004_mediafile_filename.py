# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media_manager', '0003_auto_20151205_0851'),
    ]

    operations = [
        migrations.AddField(
            model_name='mediafile',
            name='filename',
            field=models.CharField(max_length=32, default='dick'),
            preserve_default=False,
        ),
    ]
