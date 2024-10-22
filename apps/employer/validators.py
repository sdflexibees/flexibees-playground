import re
from apps.common.response_messages import field_not_null, field_not_blank, type_string, invalid_choice, invalid_url, invalid_integer_field, \
    invalid_value
from rest_framework import exceptions
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import URLValidator


class FieldValidator:
    def validate(self, value):
        raise NotImplementedError


class CharField(FieldValidator):
    """
        Custom function to validate a character field with choices.

        :param value: The value to validate.
        :param allow_null: Allow the value to be None.
        :param required: The field is required.
        :param allow_blank: Allow the value to be an empty string.
        :param choices: An optional list of allowed choices.
        :return: The processed value.
        :raises: ValueError if the value is invalid.
    """
    def __init__(self, allow_null=False, required=True, allow_blank=False, choices=None):
        self.allow_null = allow_null
        self.required = required
        self.allow_blank = allow_blank
        self.choices = choices

    def validate(self, value):
        if value is None:
            if self.allow_null:
                return
            else:
                raise ValidationError(field_not_null)
        
        if value == '':
            if self.allow_blank:
                return value
            elif not self.required:
                return None
            else:
                raise ValidationError(field_not_blank)
        
        if not isinstance(value, str):
            raise ValidationError(type_string)
        
        value = value.strip()
        if self.choices is not None and value not in self.choices:
            raise ValidationError(invalid_choice)
        return value


class URLField(FieldValidator):
    """
        Validate that the input value is a valid URL.
        
        :param value: The URL to validate.
        :raises ValidationError: If the URL is not valid.
    """
    def __init__(self, allow_null=False, required=True):
        self.allow_null = allow_null
        self.required = required

    def is_valid_url(self, url):
        """Check if the given string is a valid URL."""
        url_validator = URLValidator()
        try:
            url_validator(url)
            return True
        except DjangoValidationError:
            raise ValidationError(invalid_url)
    
    def validate(self, value):
        if value is None:
            if not self.allow_null:
                raise ValidationError(field_not_null)
        elif not self.is_valid_url(value):
            raise ValidationError(invalid_url)
        return value


class ValidationError(Exception):
    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors or {}


class BaseValidator:
    def __init__(self):
        self.fields = {}
        self.errors = {}

    def add_field(self, field_name, field_validator):
        self.fields[field_name] = field_validator

    def validate(self, data):
        self.errors = {}
        validated_data = {}
        for field_name, field_validator in self.fields.items():
            value = data.get(field_name)
            if not field_validator.required and field_name not in data:
                continue
            try:
                validated_value = field_validator.validate(value)
                validated_data[field_name] = validated_value
            except ValidationError as e:
                self.errors[field_name] = str(e)

        if self.errors:
            raise exceptions.ValidationError({'errors': self.errors})
        return validated_data

class IntegerField(FieldValidator):
    """
        Custom function to validate a character field with choices.

        :param value: The value to validate.
        :param allow_null: Allow the value to be None.
        :param required: The field is required.
        :param allow_blank: Allow the value to be an empty .
        :param choices: An optional list of allowed choices.
        :return: The processed value.
        :raises: ValueError if the value is invalid.
    """
    def __init__(self, allow_null=False, required=True, choices=None):
        self.allow_null = allow_null
        self.required = required
        self.choices = choices

    def validate(self, value):
        value = str(value)
        if value is None:
            if self.allow_null:
                return
            else:
                raise ValidationError(field_not_null)
        if value == '':
            if not self.required:
                return
            else:
                raise ValidationError(field_not_blank)
        
        if value.isdigit() == False:
            raise ValidationError(invalid_integer_field)
        
        value = int(value.strip())
        if self.choices is not None and value not in self.choices:
            raise ValidationError(invalid_choice)
        return value


class BooleanField(FieldValidator):
    """
    Custom function to validate a boolean field.

    :param allow_null: Allow the value to be None.
    :param required: The field is required.
    :return: The processed value.
    :raises: ValidationError if the value is invalid.
    """
    def __init__(self, allow_null=False, required=True):
        self.allow_null = allow_null
        self.required = required

    def validate(self, value):
        if value is None:
            if self.allow_null:
                return None
            else:
                raise ValidationError(field_not_null)
        
        if not self.required and value is None:
            return None
        
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            lower_value = value.lower()
            if lower_value in ('true', 'false'):
                return lower_value == 'true'
        raise ValidationError(invalid_value)


class FloatField(FieldValidator):
    """
    Custom function to validate a float field.

    :param allow_null: Allow the value to be None.
    :param required: The field is required.
    :param allow_blank: Allow the value to be an empty string.
    :param choices: An optional list of allowed choices.
    :return: The processed value.
    :raises: ValidationError if the value is invalid.
    """
    def __init__(self, allow_null=False, required=True, choices=None):
        self.allow_null = allow_null
        self.required = required
        self.choices = choices

    def validate(self, value):
        if value is None:
            if self.allow_null:
                return None
            else:
                raise ValidationError(field_not_null)
        
        if value == '':
            if self.required:
                raise ValidationError(field_not_blank)
            else:
                return None
        
        try:
            float_value = float(value)
        except (TypeError, ValueError):
            raise ValidationError("This field must be a valid float.")
        
        if self.choices is not None and float_value not in self.choices:
            raise ValidationError("Invalid choice.")
        
        return float_value


class ListField(FieldValidator):
    """
    Custom function to validate a list field.

    :param allow_empty: Allow the list to be empty.
    :param child_validator: A validator for the elements in the list.
    :param required: The field is required.
    :return: The processed value.
    :raises: ValidationError if the value is invalid.
    """
    def __init__(self, allow_empty=True, child_validator=None, required=True):
        self.allow_empty = allow_empty
        self.child_validator = child_validator
        self.required = required

    def validate(self, value):
        if value is None:
            if self.required:
                raise ValidationError("This field is required.")
            return None
        
        if not isinstance(value, list):
            raise ValidationError("This field must be a list.")
        
        if not value and not self.allow_empty:
            raise ValidationError("This list cannot be empty.")

        if self.child_validator is not None:
            for item in value:
                self.child_validator.validate(item)

        return value