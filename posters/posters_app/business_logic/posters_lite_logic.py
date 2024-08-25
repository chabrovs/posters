from datetime import datetime, timedelta
from django.utils import timezone


POSTERLITE_LIFETIME = timedelta(days=3)


def get_expire_timestamp() -> datetime:
    current_time = timezone.now()
    return current_time + POSTERLITE_LIFETIME