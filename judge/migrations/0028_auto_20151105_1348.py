# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0027_auto_20151014_0817'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='tags',
            field=taggit.managers.TaggableManager(verbose_name='Tags', help_text='A comma-separated list of tags.', to='taggit.Tag', blank=True, through='taggit.TaggedItem'),
        ),
        migrations.AlterField(
            model_name='test',
            name='mem_limit',
            field=models.IntegerField(verbose_name='Memory limit (MB)'),
        ),
        migrations.AlterField(
            model_name='test',
            name='score',
            field=models.DecimalField(verbose_name='Points', decimal_places=4, max_digits=8),
        ),
        migrations.AlterField(
            model_name='test',
            name='time_limit',
            field=models.DecimalField(verbose_name='Time limit (sec)', decimal_places=4, max_digits=6),
        ),
    ]
