from django.core.exceptions import ValidationError


CURRENCY_CHOICES = [
    ('USD', 'Us Dollar'),
    ('EUR', 'Euro'),
    ('RUB', 'Russian Rubble'),
    ('GBP', 'British pound'),
]

def validate_currency(value: str) -> None:
    if value not in [currency[0] for currency in CURRENCY_CHOICES]:
        raise ValidationError(f'{value} is not valid. Chose from {CURRENCY_CHOICES}')