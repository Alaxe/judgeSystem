# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0026_auto_20151014_0813'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='maxScore',
            field=models.DecimalField(default=0, decimal_places=4, max_digits=8),
        ),
        migrations.AlterField(
            model_name='solution',
            name='score',
            field=models.DecimalField(default=0, decimal_places=4, max_digits=8),
        ),
        migrations.AlterField(
            model_name='userproblemdata',
            name='maxScore',
            field=models.DecimalField(default=0, decimal_places=4, max_digits=8),
        ),
    ]
