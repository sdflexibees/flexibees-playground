from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import exceptions

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from apps.projects.models import Project, FlexiDetails, Requirement
from apps.projects.serializers import ClientDetailSerializer, FlexiDetailSerializer, \
    OtherDetailSerializer, GeneralRequirementSerializer, SalesRequirementSerializer, ContentRequirementSerializer, \
    ProjectUpdateSerializer, SalesRequirementUpdateSerializer, ContentRequirementUpdateSerializer, \
    GeneralRequirementUpdateSerializer, ProjectBaseUpdateSerializer, SalesOtherDetailSerializer, \
    GeneralOtherDetailSerializer, ClientDetailsSerializer, FlexiDetailsSerializer, \
    OtherDetailsListSerializer, ProjectInfoSerializer
from core.api_permissions import AdminAuthentication
from core.response_format import message_response
from core.response_messages import updated, mandatory_fields_missing
from core.model_choices import PROJECT_MANDATORY_FIELDS

S1_MANDATORY_FIELDS = ['min_total_experience_needed', 'max_total_experience_needed', 'educational_constraints',
                        'must_have_skills', 'company_brief', 'detailed_job_description', 'min_no_of_working_hours',
                        'max_no_of_working_hours', 'working_hours_duration_unit', 'project_duration',
                        'project_duration_unit', 'detailed_job_description', 'role']
S1_MANDATORY_FOR_SALES = ['sale_type', 'target_audience', 'describe_more', 'lead_expresses_interest']


def is_filled(data, fields):
    for each_field in fields:
        try:
            field = data[each_field]
            if (
                isinstance(field, list)
                and len(field) == 0
                or not isinstance(field, list)
                and (field == '' or field is None)
            ):
                raise exceptions.ValidationError(message_response(
                    PROJECT_MANDATORY_FIELDS[each_field] + ' may not be empty'), 400)
        except KeyError:
            return False
    return True
