import operator
from functools import reduce

from django.db.models import Case, When, Q, Value, IntegerField
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import exceptions

from apps.admin_app.models import Skill, Role
from apps.admin_app.serializers import SearchListSerializer
from apps.candidate.models import Candidate, Shortlist
from apps.candidate.serializers import AllCandidateListSerializer, ShortlistSerializer, AllCandidateListingSerializer, \
    AllCandidateCitySerializer
from apps.projects.models import Project
from core.api_permissions import AdminAuthentication
from core.pagination import paginate, query_paginate
from core.response_format import message_response
from core.response_messages import shortlisted, something_went_wrong
from core.validations import check_invalid
from core.helper_functions import api_exception_handler, api_logging
from datetime import datetime
from apps.projects.views import reopen_check
from core.helper_functions import get_filters, get_search_conditions
from core.string_constants import PROJECT_ALL_CADNDIDATES_LIST


def check_candidate_profile(candidate, error_msg=None):
    """
        Check the Candidate Profile is deleted and not
    """
    candidate_obj = get_object_or_404(Candidate, id=candidate)
    if not candidate_obj.active:
        if error_msg:
            raise exceptions.NotFound(message_response(error_msg.format(first_name=candidate_obj.first_name, last_name=candidate_obj.last_name)))
        raise exceptions.NotFound(message_response(f"Sorry you cannot see this information as candidate {candidate_obj.first_name} {candidate_obj.last_name} has deleted their profile."))
    return candidate_obj


def get_search_filters(search_term, candidate=False):
    candidate = 'candidate__' if candidate else ''
    # Removing the whitespaces from starting and ending of search term
    search_term = search_term.strip()
    search_term_split = search_term.split()
    if len(search_term_split) > 1:
        last_name = search_term_split[-1]
        first_name = ' '.join(search_term_split[:-1])
        search_term = ' '.join(search_term_split)
        name_condition = [
            ('first_name__icontains', first_name), ('last_name__icontains', last_name),
        ]
        name_reduce = reduce(operator.and_, [Q((candidate + x[0], x[1])) for x in name_condition])
    else:
        search_term = search_term
        name_condition = [
            ('first_name__icontains', search_term), ('last_name__icontains', search_term),
        ]
        name_reduce = reduce(operator.or_, [Q((candidate + x[0], x[1])) for x in name_condition])
    conditions = [
        ('roles__tag_name__icontains', search_term),
        ('skills__tag_name__icontains', search_term),
        ('legacy_skills__icontains', search_term),
        ('skills_resume__icontains', search_term),
        ('legacy_last_role__icontains', search_term),
        ('legacy_prior_roles__icontains', search_term),
        ('legacy_last_employer__icontains', search_term),
        ('legacy_prior_employers__icontains', search_term),
        ('city__icontains', search_term),
        ('phone__icontains', search_term),
        ('email__icontains', search_term),
        ('employmentdetail__company__icontains', search_term),
        ('employmentdetail__role__tag_name__icontains', search_term)
    ]
    common_reduce = reduce(operator.or_, [Q((candidate + x[0], x[1])) for x in conditions])
    return common_reduce, name_reduce