# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0025_auto_20151014_0809'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testresult',
            name='score',
            field=models.DecimalField(max_digits=8, decimal_places=4),
        ),
    ]
