# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0028_auto_20151105_1348'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='problem',
            options={'ordering': ['-id'], 'permissions': (('problem_retest', 'Can start a retest'), ('problem_visibility', "Can change problem's visibility"), ('problem_hidden', 'Can see hidden problems'), ('add_media_to_problem', 'Can upload media for the problem'))},
        ),
        migrations.AddField(
            model_name='problem',
            name='statement_language',
            field=models.CharField(verbose_name='Language', choices=[('html', 'HTML'), ('md', 'Markdown')], max_length=8, default='html'),
        ),
        migrations.AlterField(
            model_name='problem',
            name='statement',
            field=models.TextField(blank=True, verbose_name='Problem statement'),
        ),
        migrations.AlterField(
            model_name='problem',
            name='title',
            field=models.CharField(default='New Problem', verbose_name='Title', max_length=64),
        ),
    ]
