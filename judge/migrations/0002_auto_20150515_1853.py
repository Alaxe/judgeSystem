# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='statement',
            field=models.TextField(verbose_name='Problem statement'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='solution',
            name='source',
            field=models.TextField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='test',
            name='stdin',
            field=models.TextField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='test',
            name='stdout',
            field=models.TextField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='test',
            name='time_limit',
            field=models.DecimalField(max_digits=6, decimal_places=4),
            preserve_default=True,
        ),
    ]
