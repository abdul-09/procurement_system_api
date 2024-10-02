from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab, schedule
from procurement_system import settings


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'procurement_system.settings')


app = Celery('procurement_system')

app.conf.beat_schedule = {

    'close_expired_tenders': {
        'task': 'api.tasks.close_expired_tenders',
        'schedule': crontab(hour='22', day_of_week='*'),  # Run every 10pm
    },
}


app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
