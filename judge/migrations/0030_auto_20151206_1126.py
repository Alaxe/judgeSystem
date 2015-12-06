# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0029_auto_20151206_0952'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestGroup',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(verbose_name='Name of test group', max_length=32)),
                ('score', models.DecimalField(verbose_name='Points', max_digits=6, decimal_places=2)),
                ('problem', models.ForeignKey(to='judge.Problem')),
            ],
        ),
        migrations.AlterField(
            model_name='test',
            name='score',
            field=models.DecimalField(verbose_name='Points', max_digits=6, decimal_places=2),
        ),
        migrations.AddField(
            model_name='test',
            name='test_group',
            field=models.ForeignKey(to='judge.TestGroup', null=True),
        ),
    ]
