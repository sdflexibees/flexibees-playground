import uuid
import string
from random import choice
from rest_framework.views import exception_handler
from django.http import Http404
from .response_messages import object_does_not_exist, invalid_input
from rest_framework.exceptions import ValidationError


def upload_image(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex, ext)
    return 'images/{0}/{1}/'.format(instance.__class__.__name__, filename)


def upload_file(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex, ext)
    return 'files/{0}/{1}/'.format(instance.__class__.__name__, filename)


def generate_password():
    alphabet = string.ascii_letters + string.digits
    while True:
        value = "".join(choice(alphabet) for _ in range(6))
        return value


def generate_otp():
    alphabet = string.digits
    while True:
        value = "".join(choice(alphabet) for _ in range(4))
        return value


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.py.
    response = exception_handler(exc, context)

    if isinstance(exc, Http404):
        custom_response_data = {
            'statusCode': 404,
            'data': {
                'message': object_does_not_exist
            }
        }
        response.data = custom_response_data # set the custom response.py data on response.py object

    return response


def custom_error(error_data):
    for key in error_data:
        key_name = key.replace('_', ' ').capitalize()
        return {"message": error_data[key][0].replace('This', key_name).
            replace('this', key_name).rstrip('.')}
    return None


def make_lower(_class, fields):
    for field_name in fields:
        val = getattr(_class, field_name, False)
        if val:
            setattr(_class, field_name, val.lower())
    return True


def make_title(_class, fields):
    for field_name in fields:
        val = getattr(_class, field_name, False)
        if val:
            setattr(_class, field_name, val.title())
    return True


def make_upper(_class, fields):
    for field_name in fields:
        val = getattr(_class, field_name, False)
        if val:
            setattr(_class, field_name, val.upper())
    return True

def send_validation_error(e):
    validation_error_message = invalid_input
    if isinstance(e, ValidationError):
        error = e.args[0]
        if 'errors' in error:
            validation_error_message = error.get("errors")
        else:
            validation_error_message = error.get('message')
    return validation_error_message