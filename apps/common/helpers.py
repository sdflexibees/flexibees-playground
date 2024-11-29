from .constants import DOMAINS, LOGIN, MOBILE_CHANGE, MOBILE_OTP_MESSAGE, PROD
from apps.employer.models import Employer
from django.db.models import Q
from core.emails import email_send
from core.response_format import message_response
from core.sms import send_sms
from flexibees_finance.settings import ENV
from rest_framework import exceptions
from .response_messages import invalid_input, invalid_email, user_exists



def validate_employer(employer, request_type):
    if request_type == MOBILE_CHANGE and (not employer.additional_info or not employer.additional_info.get("mobile")):
        raise exceptions.ValidationError(message_response(invalid_input), 400)
    return True


def update_verifications(employer, request_type):
    # If the OTP is correct and the email is not verified, mark email as verified.
    if request_type!=LOGIN and employer.user.email and not employer.user.email_verified:
        employer.user.email_verified = True
    # If the OTP is correct and the phone is not verified, mark phone as verified.
    if request_type!=LOGIN and employer.user.mobile and not employer.user.phone_verified:
        employer.user.phone_verified = True

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


def send_email_verification(email, username, otp, template, subject):
    # Implement email sending logic with subject, template, and context
    if ENV == PROD:
        email_send(subject=subject, template=template, recipient=[email], context={'username': username, 'otp': otp})

def send_sms_verification(country_code, mobile, otp):
    # Implement SMS sending logic with message formatting
    if ENV == PROD:
        message = MOBILE_OTP_MESSAGE.format(otp)
        send_sms(country_code, mobile, message)


def validate_email(value):
    """
    Validate the email address.
    """
    # Use Django's built-in email validator
    domain = value.split('@')[-1]
    if domain in DOMAINS:
        raise exceptions.ValidationError(message_response(invalid_email), 400)
    if Employer.objects.filter(user__email__iexact=value, is_active=True).exists():
        raise exceptions.ValidationError(message_response(user_exists), 400)
