import re
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

from rest_framework import exceptions

from core.response_format import message_response
from core.response_messages import invalid_input


def check_invalid(fields):
    if None in fields:
        raise exceptions.ValidationError(message_response(invalid_input), 400)


mobile_regex = RegexValidator(regex=r'^\d{7,15}$',
                              message=_("Please Enter correct Contact no.")
                              )

password_regex = r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[^a-zA-Z0-9])(?!.*\s).{6,15}$'
message='6 to 15 characters which contain at least one lowercase letter, one \
uppercase letter, one numeric digit, and one special character'

