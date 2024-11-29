from functools import wraps
from apps.projects.models import Pricing
from core.constants import REQUEST_INDEX
from core.extra import send_validation_error
from flexibees_finance.settings import MIN_HOURS_FOR_MY_TYPICAL_DAY
from datetime import datetime
from apps.availability.models import CandidateAvailability
from apps.candidate.models import Candidate
from rest_framework import exceptions
from django.core.exceptions import ObjectDoesNotExist
from core.response_format import message_response
from flexibees_finance.settings import APP_VERSION
from core.response_messages import update_app, closed_project, suspended_project, something_went_wrong,\
email_user_exists, link_expired, email_already_verified
import logging
from flexibees_finance.settings import CLOSED_PROJECT_STATUS, SUSPENDED_PROJECT_STATUS, HOURS_A_DAY
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


def get_filters(filters, role=None):
    try:
        filter_query = {}
        if filters:
            filter_query.update({'roles__in': filters.get('roles')}) if len(filters.get('roles', [])) != 0 \
                else filter_query
            filter_query.update({'skills__in': filters.get('skills')}) if len(filters.get('skills', [])) != 0 \
                else filter_query
            filter_query.update({'active_projects__in': filters.get('active_projects')}) if len(filters.get(
                'active_projects', [])) != 0 else filter_query
            filter_query.update({'total_available_hours__in': filters.get('total_available_hours')}) if len(
                filters.get('total_available_hours', [])) != 0 else filter_query
            filter_query.update({'flexibees_selected__in': filters.get('flexibees_selected')}) if len(
                filters.get('flexibees_selected', [])) != 0 else filter_query
            if filters.get('years_of_experience'):
                years_of_experience = filters.get('years_of_experience')
                if years_of_experience.get('min') and years_of_experience.get('min') != "":
                    filter_query.update({'total_year_of_experience__gte': years_of_experience.get('min')})
                if years_of_experience.get('max') and years_of_experience.get('max') != "":
                    filter_query.update({'total_year_of_experience__lte': years_of_experience.get('max')})
            if role:
                if filters.get('relevant_experience'):
                    relevant_experience = filters.get('relevant_experience')
                    if relevant_experience.get('min') and relevant_experience.get('min') != "":
                        filter_query.update({'relevantexp__r' + role + '__gte': relevant_experience.get('min')})
                    if relevant_experience.get('max') and relevant_experience.get('max') != "":
                        filter_query.update({'relevantexp__r' + role + '__lte': relevant_experience.get('max')})
            else:
                filter_query.update({'city__in': filters.get('cities')}) if len(filters.get('cities', [])) != 0 \
                else filter_query
                filter_query.update({'years_of_break__in': filters.get('years_of_break')}) if len(
                    filters.get('years_of_break', [])) != 0 else filter_query
        return filter_query
    except Exception as e:
        log_data = [f"info|| {datetime.now()}: Exception occured in filters"]
        log_data.append(f"error|| {e}")
        api_logging(log_data)
        return False

    
def get_search_conditions(search_fields, search_term):
    end = len(search_fields)-1
    search_conditions = ''
    for pos, field in enumerate(search_fields):
        if field=='skills_resume':
            search_conditions += f"""
            EXISTS (
            SELECT 1
            FROM unnest(skills_resume) AS skill
            WHERE lower(skill) LIKE lower('%{search_term}%')
            )"""
        elif field=='skill':
            search_conditions += f"""EXISTS (
            SELECT 1
            FROM candidate_candidate_skills
            INNER JOIN admin_app_skill ON candidate_candidate_skills.skill_id = admin_app_skill.id
            WHERE candidate_candidate.id = candidate_candidate_skills.candidate_id
            AND lower(admin_app_skill.tag_name) LIKE lower('%{search_term}%')
            )"""
        elif field=='role':
            search_conditions += f"""EXISTS (
            SELECT 1
            FROM candidate_candidate_roles
            INNER JOIN admin_app_role ON candidate_candidate_roles.role_id = admin_app_role.id
            WHERE candidate_candidate.id = candidate_candidate_roles.candidate_id
            AND lower(admin_app_role.tag_name) LIKE lower('%{search_term}%')
            )"""
        elif field=='employment_detail':
            search_conditions += f"""EXISTS (
            SELECT 1
            FROM candidate_employmentdetail
            WHERE candidate_candidate.id = candidate_employmentdetail.candidate_id
            AND (
            lower(candidate_employmentdetail.company) LIKE lower('%{search_term}%') OR EXISTS
            (
            SELECT 1
            FROM admin_app_role
            WHERE id = candidate_employmentdetail.role_id
            AND (
            lower(tag_name) LIKE lower('%{search_term}%')
            )
            )
            )
            )"""
        elif field in ['first_name', 'last_name', 'legacy_skills', 'legacy_last_role', 'legacy_prior_roles', 'legacy_last_employer', 'legacy_prior_employers', 'city', 'phone', 'email']:
            search_conditions += f"lower({field}) LIKE lower('%{search_term}%')"
        if end != pos:
            search_conditions += ' OR '
    return search_conditions
