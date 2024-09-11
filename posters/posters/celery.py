from __future__ import absolute_import, unicode_literals
import os 
from celery import Celery

# Enable Django virtual for the Celery cli
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'posters.settings')

# Create an app instance
# app = Celery('posters', broker='amqp://guest:guest@localhost//')
app = Celery('posters',)


# Django-celery-beat scheduler
app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'

# Add Django settings module as the configuration source for Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Enable automatic task discovery in the Django applications
app.autodiscover_tasks()