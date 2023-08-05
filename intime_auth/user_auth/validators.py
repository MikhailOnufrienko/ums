import re
from django.core.exceptions import ValidationError


def validate_phone_number(value: str) -> None:
    pattern = r'^\d{10, 12}$'
    if not re.match(pattern, value):
        raise ValidationError(
            'Invalid phone number. It should be'
            'from 10 to 15 digits without any separators.'
        )
