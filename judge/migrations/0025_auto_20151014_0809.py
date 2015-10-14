# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0024_auto_20150930_2050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='score',
            field=models.DecimalField(max_digits=8, decimal_places=4),
        ),
    ]
