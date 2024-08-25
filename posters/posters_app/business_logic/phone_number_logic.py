import phonenumbers
from django.core.exceptions import ValidationError


#region: EXCEPTIONS

class InvalidPhoneNumberException(Exception):
    def __init__(self, phone_number: str | None = None, message: str = 'The provided phone number is invalid') -> None:
        self.phone_number = phone_number
        self.message = message
        super().__init__(self.phone_number, self.message)

    def __str__(self) -> str:
        return f"[Exception MSG]: {self.message}\nProvided phone number ({self.phone_number})"
    
    
class InvalidPhoneNumberValidation(ValidationError):
    def __init__(self, phone_number: str | None, message: str = 'Invalid phone number') -> None:
        self.phone_number = phone_number
        self.message = message
        super().__init__(self.phone_number, self.message)

    def __str__(self) -> str:
        return f"[Exception MSG]: {self.message}\nProvided phone number ({self.phone_number})"

#endregion

#region: BUSINESS LOGIC

def standardize_phone_number(phone_number: str, region='RU') -> str:
    """
    Standardize phone number before writing it to the database.
    If a phone number is not valid, raise an exception 
    (#NOTE: Alter this exception before production. The exception must not the cause the app crush)
    :Param phone_number: Users provided phone number.
    :Param region <default='RU'>: Region the number origin.
    """
    
    try:
        phone_number = phonenumbers.parse(phone_number, region=region)

        if phonenumbers.is_valid_number(phone_number):
            formatted_phone_number = phonenumbers.format_number(
                phone_number,
                phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )
            return formatted_phone_number
        else:
            return None
        
    except phonenumbers.NumberParseException:
        raise InvalidPhoneNumberException(phone_number)
    
#endregion
 
#region: VALIDATORS

def validate_phone_number(phone_number: str | None) -> None:
    if phone_number == None:
        raise InvalidPhoneNumberValidation(phone_number)
    
#endregion 