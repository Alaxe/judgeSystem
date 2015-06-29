# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0008_auto_20150628_1440'),
    ]

    operations = [
        migrations.AddField(
            model_name='userproblemdata',
            name='last_submit',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 28, 14, 17, 34, 984804, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
