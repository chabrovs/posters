from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .email import send_verification_code_email

@shared_task(name="send_verification_code")
def send_verification_code_task(code: int | str):
    return send_verification_code_email(code)