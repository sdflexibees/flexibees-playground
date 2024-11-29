import datetime
import json
from django.db.models import Q, F
from apps.admin_app.views import api_logging
from apps.candidate.models import FlexifitFeedback
from apps.common.constants import DRAFT_JOB_PENDING, PENDING_STATUS
from apps.employer.constants import FLEXIFIT_INTERVIEW_CLEARED, HIGHEST_PRIORITY, JOB_CANDIDATE_REJECTED, MAX_CANDIDATES, MAX_DRAFT_CANDIDATES
from apps.employer.models import CandidateJobNotes, CandidateJobStatus, Job, JobCustomRoleSkills, SkippedCandidate
from apps.employer.validation import JobListFilterValidator
from core.helper_functions import get_sort
from django.contrib.postgres.aggregates import ArrayAgg
from apps.employer.constants import DEFAULT_CURRENCY_SYMBOL, FLEXIFIT_INTERVIEW_CLEARED
from apps.employer.models import CandidateJobNotes, CandidateJobStatus, Company, Job, JobCustomRoleSkills, RolesMinMaxPricing, SkippedCandidate


def get_search_term_filter(value):
    query = Q()
    if value:
        query |= Q(function__tag_name__icontains=value)
        query |= Q(role__tag_name__icontains=value)
        query |= Q(skills__tag_name__icontains=value)
        query |= Q(jobcustomroleskills__role__role_name__icontains=value)
        query |= Q(jobcustomroleskills__skill__skill_name__icontains=value)
    return query


def get_draft_search_term_filter(value):
    """
    Creates a query to search within the 'details' JSON field of a DraftJob object.
    
    Args:
        value (str): The search term to filter by.
        
    Returns:
        Q: A Q object representing the query filter.
    """
    query = Q()
    if value:
        # Example of searching specific keys inside 'details'
        query |= Q(details__custum_role__icontains=value)
        query |= Q(details__existing_role__icontains=value)
        query |= Q(details__custom_skills__skill_name__icontains=value)
        query |= Q(details__existing_skills__skill_name__icontains=value)
        query |= Q(details__function_name__icontains=value)
    
    return query

def get_job_listing_query_filters(filters, sort, is_all_jobs, user):
    """
    filters for jobs list 
    """
    filters = JobListFilterValidator().validate(filters)
    filter_dict = {
        'status': lambda x: Q(status=x),
        'statusus': lambda x: Q(status__in=x),
        'search': lambda x : get_search_term_filter(x)
    }
    draft_query = Q()
    if is_all_jobs:
        draft_query = Q(employer=user)
        draft_query &= Q(status=PENDING_STATUS)
    query = Q()
    for filter in filters:
        if filter_dict.get(filter):
            query &= filter_dict[filter](filters[filter])
            if is_all_jobs and filter=='search':
                draft_query &= get_draft_search_term_filter(filters[filter])

    values = ['id', 'status', 'details', 'updated_at']
    other_values = {
        'role_name': F('role__tag_name'),
        'role_id': F('role__id'),
        'function': F('function__tag_name'),
        'custom_role': F('jobcustomroleskills__role__role_name'),
        'custom_role_id': F('jobcustomroleskills__role__id'),
    }
    sort = get_sort(sort)
    return query, draft_query, values, other_values, sort

def check_duplicate(candidate, job, user):
    """
    check candidate is eligible and not in skipped and job 
    """
    job_ready_candidate = FlexifitFeedback.objects.filter(recommendation=FLEXIFIT_INTERVIEW_CLEARED, flexifit__candidate__id=candidate, flexifit__candidate__active=True).exists()
    candidate_job_exists = CandidateJobStatus.objects.filter(candidate__id=candidate, job__id=job).exists()
    skipped_exists = SkippedCandidate.objects.filter(candidate__id=candidate, job__id=job).exists()
    project_check = Job.objects.filter(id=job, employer=user).exists()
    return not job_ready_candidate or candidate_job_exists or skipped_exists or not project_check

def get_draft_query(filters, user):
    """
    Query for draft listing
    """
    query = Q(employer=user)
    query &= Q(status=DRAFT_JOB_PENDING)
    query &= Q(is_active=True)
    # filters 
    filter_dict = {
        'search': lambda x : get_draft_search_term_filter(x)
    }
    for filter in filters:
        if filter_dict.get(filter):
            query &= filter_dict[filter](filters[filter])
    return query

