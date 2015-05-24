# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('judge', '0003_confirmation'),
    ]

    operations = [
        migrations.CreateModel(
            name='PassReset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=32, default='RAH57XKKVDT4CWPRYRUH565UMNCEJGVW')),
                ('created', models.DateTimeField()),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='solution',
            options={'ordering': ['-submit_date']},
        ),
        migrations.AlterModelOptions(
            name='testresult',
            options={'ordering': ['test']},
        ),
        migrations.AddField(
            model_name='confirmation',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 24, 13, 33, 32, 620584, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='confirmation',
            name='code',
            field=models.CharField(max_length=32, default='OFTOJYLHCJTLRYZBBNI6YUTZBXUSCPCF'),
            preserve_default=True,
        ),
    ]
