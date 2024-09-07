from django.template import Context
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from typing import Callable


def send_verification_code_email(email: str, code: int | str) -> Callable:
    # Create context
    context = {
        'email': email,
        'code': code
    }

    email_subject = "Posters Login Code."
    email_body = render_to_string('email_service/auth_account_login.txt', context=context)
    email = EmailMessage(
        email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [email, ],
    )

    return email.send(fail_silently=False)