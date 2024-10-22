from functools import wraps
from apps.projects.models import Pricing
from core.constants import REQUEST_INDEX
from core.extra import send_validation_error
from flexibees_candidate.settings import MIN_HOURS_FOR_MY_TYPICAL_DAY
from datetime import datetime
from apps.availability.models import CandidateAvailability
from apps.candidate.models import Candidate
from rest_framework import exceptions
from django.core.exceptions import ObjectDoesNotExist
from core.response_format import message_response
from flexibees_candidate.settings import APP_VERSION
from core.response_messages import update_app, closed_project, suspended_project, something_went_wrong,\
email_user_exists, link_expired, email_already_verified
import logging
from flexibees_candidate.settings import CLOSED_PROJECT_STATUS, SUSPENDED_PROJECT_STATUS, HOURS_A_DAY
import string
from random import choice
from django.utils import timezone
from django.db.models import OneToOneField, ManyToManyField, Field
from rest_framework.response import Response


def api_logging(log_data):
    """
    Function used to log all the API requests and responses along with error if any.
    Creates log files on daily basis.
    Params:
    1. log_data: list of individual logs having log type and message.
    """
    # Create Log file in logs folder:
    log_dir = 'logs'
    logging.basicConfig(
        filename=f"{log_dir}/api_requests_{datetime.now().date()}.log", level=logging.DEBUG)
    try:
        for log in log_data:
            message = log.split("||")
            if message[0] == 'info':
                logging.info(message[1])
            else:
                logging.error(message[1])
    except Exception as e:
        logging.error(f"Log function error: {str(e)}")
    logging.info("=" * 150)
    return True

def min_hours_filled_in_my_typical_day(candidate_id):
    try:
        candidate_availability_query = CandidateAvailability.objects.filter(candidate=candidate_id, active=True)
        total_hours = 0
        if list(candidate_availability_query) :
            for availability_query in candidate_availability_query:
                start = datetime.combine(datetime.now(), availability_query.start_time)
                end = datetime.combine(datetime.now(), availability_query.end_time)
                duration = end - start
                hours = duration.total_seconds() / 3600
                total_hours+=hours
        return total_hours >= MIN_HOURS_FOR_MY_TYPICAL_DAY
    except Exception as e :
        log_data = [f"info|| {datetime.now()}: Exception occured min_hours_filled_in_my_typical_day function"]
        log_data.append(f"error|| {e}")
        api_logging(log_data)
        return False

def check_version(request):
   version = request.META.get('HTTP_VERSION')
   if version and  version in APP_VERSION:
       return True
   else:
       raise exceptions.ValidationError(message_response(update_app), 400)

def check_email(email):
    try:
        Candidate.objects.get(email__iexact=email, active=True)
        raise exceptions.ValidationError(message_response(email_user_exists), 400)
    except ObjectDoesNotExist:
        pass

def generate_otp():
    alphabet = string.digits
    return "".join(choice(alphabet) for _ in range(4))

def list_field_names(model, exclude=[]):
    return [field.name for field in model._meta.get_fields() 
            if (isinstance(field, Field) or isinstance(field, OneToOneField) or isinstance(field, ManyToManyField) )
            and field.name not in exclude 
        ]

def get_sort(sort):
    """
    if not sort value, sort by id desc
    """
    sort_by = '-id'
    if sort:
        sort_by = sort
    return sort_by

def api_exception_handler(api_name, is_staticmethod=True):
    """
    Decorator to catch api exception
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            request = None
            # Determine the position of the request object
            if len(args) > REQUEST_INDEX:
                if is_staticmethod:
                    request = args[0]
                else:
                    request = args[1]
            elif 'request' in kwargs:
                request = kwargs['request']
            
            log_data = [f"info|| {datetime.now()}: {api_name} API called"]
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if request:
                    error_message = send_validation_error(e)
                    context = {
                        "request_url": request.META['PATH_INFO'], "error": str(e), "payload": request.data
                    }
                    log_data.append(f"info || context :{context}")
                    log_data.append("LINE_BREAK")
                    api_logging(log_data)
                    return Response(message_response(error_message), status=400)
                else:
                    # Handle the case where request is not found
                    log_data.append(f"error || request object not found in {api_name} API")
                    log_data.append("LINE_BREAK")
                    api_logging(log_data)
                    return Response({"error": "Request object not found"}, status=400)
        return wrapper
    return decorator