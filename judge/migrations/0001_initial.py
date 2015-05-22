# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=64, verbose_name='Title')),
                ('statement', models.CharField(max_length=4096, verbose_name='Problem statement')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Solution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source', models.CharField(max_length=2048)),
                ('submit_date', models.DateTimeField(verbose_name='Date of submition')),
                ('grader_message', models.CharField(max_length=128)),
                ('problem', models.ForeignKey(to='judge.Problem')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stdin', models.CharField(max_length=2048)),
                ('stdout', models.CharField(max_length=2048)),
                ('time_limit', models.FloatField()),
                ('mem_limit', models.IntegerField()),
                ('points', models.IntegerField()),
                ('problem', models.ForeignKey(to='judge.Problem')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TestResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.CharField(max_length=64)),
                ('score', models.IntegerField()),
                ('solution', models.ForeignKey(to='judge.Solution')),
                ('test', models.ForeignKey(to='judge.Test')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
