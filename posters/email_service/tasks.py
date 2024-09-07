from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from .email import send_verification_code_email


@shared_task(bind=True, name="send_verification_code", max_retries=3, default_retry_delay=30)
def send_verification_code_task(self, email: str, code: int | str):
    try:
        send_verification_code_email(email, code)
    except Exception as exc:
        try:
            raise self.retry(exc=exc)
        except MaxRetriesExceededError:
            print(f"Failed to send the verification code after ({self.max_retries})")

