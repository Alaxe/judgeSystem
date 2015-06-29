# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0003_auto_20150628_1423'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserStatts',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('solvedProblems', models.IntegerField(default=0)),
                ('triedProblems', models.IntegerField(default=0)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='confirmation',
            name='code',
            field=models.CharField(default='9U4NEUTZ3NO1THTXDY52TOIJH1XEI3PT', max_length=32),
        ),
        migrations.AlterField(
            model_name='confirmation',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 28, 11, 40, 15, 776444, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='passreset',
            name='code',
            field=models.CharField(default='IFJDQRJ06WCAP2YE9VDBAN4QAG4KGEUO', max_length=32),
        ),
        migrations.AlterField(
            model_name='passreset',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 28, 11, 40, 15, 777097, tzinfo=utc)),
        ),
    ]
