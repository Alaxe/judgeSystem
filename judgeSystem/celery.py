from __future__ import absolute_import

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'judgeSystem.settings')

app = Celery('tasks')

from django.conf import settings
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.update(
    CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
    #BROKER_URL = 'django://',
    CELERY_TASK_SERIALIZER = 'pickle',
    CELERY_ACCEPT_CONTENT = ['pickle'],
    CELERY_TASK_RESULT_EXPIRES=3600,
)
