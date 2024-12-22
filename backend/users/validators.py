from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.exceptions import ValidationError

from api.constants import FORBIDDEN_NAME, RESOLVED_CHARS


class UsernameValidator(ASCIIUsernameValidator):
    message = (RESOLVED_CHARS)


def validate_username(value):
    if value.lower() == 'me':
        raise ValidationError(FORBIDDEN_NAME)
    return value
