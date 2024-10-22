from .constants import DOMAINS, LOGIN, MOBILE_CHANGE, MOBILE_OTP_MESSAGE, PROD
from apps.employer.models import Employer
from django.db.models import Q
from core.emails import email_send
from core.response_format import message_response
from core.sms import send_sms
from flexibees_candidate.settings import ENV
from rest_framework import exceptions
from .response_messages import invalid_input, invalid_email, user_exists


def validation_error_data(e):
    """
    This function checks for validation errors and returns the appropriate message.
    If a ValidationError occurs, it returns the error details as a dictionary. Otherwise, it returns a string.

    Parameters:
    e (Exception): The exception object to check for validation errors.

    Returns:
    dict or str: The validation error details as a dictionary if a ValidationError occurs, otherwise a string.
    """
    validation_error_message = invalid_input
    if isinstance(e, exceptions.ValidationError):
        lenght = len(e.args)
        if lenght >= 1:
            validation_error_message = e.args[0].get('errors')
    return validation_error_message