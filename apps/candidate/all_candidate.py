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
from core.helper_functions import api_logging
from datetime import datetime


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

    permission_classes = (AdminAuthentication,)
    serializer_class = SearchListSerializer

    @staticmethod
    def project_all_candidate_list(request, project, page_size=10, page=1):
        project_query = get_object_or_404(Project, id=project, active=True)
        try:
            flexi_data = project_query.flexidetails_set.get_or_create()[0]
            reopen_check(project_query, request.role)
            role = str(project_query.role.id)
            must_have_skills = list(project_query.requirement_set.get_or_create()[0].must_have_skills.
            values_list('id', flat=True))
            search_term = request.data.get('search_term', '')
            filters = request.data.get('filter_data')
            matching = filters.get('matching', False)
            search_fields = request.data.get('search_fields',[])
            filter_query = get_filters(filters, role)
            applied_filters = apply_filters(filter_query, role)
            search_term_split = search_term.split()
            if len(search_term_split) > 1:
                last_name = search_term_split[-1]
                first_name = ' '.join(search_term_split[:-1])
            city_filter = f"city = '{flexi_data.selected_city}' AND" if (flexi_data.is_travel_required and flexi_data.selected_city !='') else ''
            matching_filter = f"""AND(
                ({ city_filter}
                total_available_hours >= {flexi_data.min_no_of_working_hours} AND EXISTS (
                SELECT 1
                FROM candidate_candidate_skills
                WHERE candidate_candidate.id = candidate_candidate_skills.candidate_id
                AND candidate_candidate_skills.skill_id IN ({", ".join(str(item) for item in must_have_skills)})
                )) OR
                EXISTS (
                SELECT 1
                FROM candidate_candidate_skills
                WHERE candidate_candidate.id = candidate_candidate_skills.candidate_id
                AND candidate_candidate_skills.skill_id IN ({", ".join(str(item) for item in must_have_skills)})
                ) 
                )""" if matching else ''
            name_filter = f"lower(first_name) LIKE lower('%{first_name if len(search_term_split) > 1 else search_term}%') {'AND' if len(search_term_split) > 1 else 'OR'} lower(last_name) LIKE lower('%{last_name if len(search_term_split) > 1 else search_term}%')"
            search_filters = f"AND ({get_search_conditions(search_fields, search_term)} )" if len(search_fields) else f'''AND (
                (
                {name_filter}
                )
                OR (
                lower(legacy_skills) LIKE lower('%{search_term}%')
                OR lower(legacy_last_role) LIKE lower('%{search_term}%')
                OR lower(legacy_prior_roles) LIKE lower('%{search_term}%')
                OR lower(legacy_last_employer) LIKE lower('%{search_term}%')
                OR lower(legacy_prior_employers) LIKE lower('%{search_term}%')
                OR lower(city) LIKE lower('%{search_term}%')
                OR lower(phone) LIKE lower('%{search_term}%')
                OR lower(email) LIKE lower('%{search_term}%')
                OR EXISTS (
                SELECT 1
                FROM unnest(skills_resume) AS skill
                WHERE lower(skill) LIKE lower('%{search_term}%')
                )
                OR EXISTS (
                SELECT 1
                FROM candidate_candidate_skills
                INNER JOIN admin_app_skill ON candidate_candidate_skills.skill_id = admin_app_skill.id
                WHERE candidate_candidate.id = candidate_candidate_skills.candidate_id
                AND lower(admin_app_skill.tag_name) LIKE lower('%{search_term}%')
                )
                OR EXISTS (
                SELECT 1
                FROM candidate_candidate_roles
                INNER JOIN admin_app_role ON candidate_candidate_roles.role_id = admin_app_role.id
                WHERE candidate_candidate.id = candidate_candidate_roles.candidate_id
                AND lower(admin_app_role.tag_name) LIKE lower('%{search_term}%')
                )
                OR EXISTS (
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
                )
                )
                )'''
            data_query = f"""
            SELECT
                candidate_candidate.id,
                candidate_candidate.first_name,
                candidate_candidate.city as Candidate_city,
                candidate_candidate.total_year_of_experience,
                candidate_candidate.flexibees_selected,
                candidate_candidate.active_projects,
                candidate_candidate.hire,
                candidate_candidate.timeline_completed,
                candidate_candidate.total_available_hours,
                {f"COALESCE((candidate_candidate.relevantexp->'r{role}')::float, 0) AS relevant_experience, " if role else 'none AS relevant_experience,'}
                COALESCE((
                SELECT JSON_AGG(
                JSON_BUILD_OBJECT(
                'id', admin_app_role.id,
                'name', admin_app_role.tag_name
                )::json
                )
                FROM candidate_candidate_roles
                INNER JOIN admin_app_role ON candidate_candidate_roles.role_id = admin_app_role.id
                WHERE candidate_candidate.id = candidate_candidate_roles.candidate_id
                ), '[]'::json) AS roles,
                COALESCE((
                SELECT JSON_AGG(
                JSON_BUILD_OBJECT(
                'id', admin_app_skill.id,
                'name', admin_app_skill.tag_name,
                'function', admin_app_skill.function_id
                )::json
                )
                FROM candidate_candidate_skills
                INNER JOIN admin_app_skill ON candidate_candidate_skills.skill_id = admin_app_skill.id
                WHERE candidate_candidate.id = candidate_candidate_skills.candidate_id
                ), '[]'::json) AS skills,
                CASE
                WHEN EXISTS (
                SELECT 1
                FROM candidate_candidate_skills
                WHERE candidate_candidate.id = candidate_candidate_skills.candidate_id
                AND candidate_candidate_skills.skill_id IN ({", ".join(str(item) for item in must_have_skills)})
                )
                {f"AND candidate_candidate.city = '{flexi_data.selected_city}'" if (flexi_data.is_travel_required and flexi_data.selected_city != '') else ''}
                AND candidate_candidate.total_available_hours >= {flexi_data.min_no_of_working_hours} THEN true
                ELSE false
                END AS must_have_skills,
                CASE
                WHEN candidate_candidate.total_available_hours >= {flexi_data.min_no_of_working_hours} THEN 'green'
                ELSE 'red'
                END AS availability
            FROM 
                candidate_candidate
            WHERE
                candidate_candidate.active = TRUE
                AND candidate_candidate.hire = TRUE
                {' AND (' + applied_filters + ')' if applied_filters else ''}
                {matching_filter if matching else ''}
                AND NOT EXISTS (
                SELECT 1
                FROM candidate_shortlist
                WHERE 
                candidate_shortlist.candidate_id = candidate_candidate.id
                AND candidate_shortlist.project_id = {project}
                )
                {search_filters if search_term else ''}
            ORDER BY
                CASE
                WHEN { city_filter}
                total_available_hours >= {flexi_data.min_no_of_working_hours} AND EXISTS (
                SELECT 1
                FROM candidate_candidate_skills
                WHERE candidate_candidate.id = candidate_candidate_skills.candidate_id
                AND candidate_candidate_skills.skill_id IN ({", ".join(str(item) for item in must_have_skills)})
                ) THEN 0
                WHEN EXISTS (
                SELECT 1
                FROM candidate_candidate_skills
                WHERE candidate_candidate.id = candidate_candidate_skills.candidate_id
                AND candidate_candidate_skills.skill_id IN ({", ".join(str(item) for item in must_have_skills)})
                ) THEN 1
                ELSE 2
                END,
                id DESC 
            """
            count_query = f"""
                SELECT 
                    COUNT(candidate_candidate.id)
                FROM 
                    candidate_candidate
                {f"INNER JOIN candidate_candidate_skills  ON candidate_candidate.id = candidate_candidate_skills.candidate_id AND candidate_candidate_skills.skill_id IN ({f', '.join(str(item) for item in must_have_skills)})" if matching else ''}
                WHERE
                    candidate_candidate.active = TRUE
                    AND candidate_candidate.hire = TRUE
                    {' AND (' + applied_filters + ')' if applied_filters else ''}
                    {matching_filter if matching else ''}
                    AND NOT EXISTS (
                    SELECT 1
                    FROM candidate_shortlist
                    WHERE candidate_shortlist.candidate_id = candidate_candidate.id
                    AND candidate_shortlist.project_id = {project}
                    )
                    {search_filters if search_term else ''}
            """
            result = query_paginate(data_query, count_query, page=page, page_size=page_size)
            context = {
                'result':result
            }
            return Response(context)
        except Exception as e:
            log_data = [f"info|| {datetime.now()}: Exception occured in project all candidates list raw query api"]
            log_data.append(f"error|| {e}")
            api_logging(log_data)
            return Response(message_response(something_went_wrong))
    
    @staticmethod
    def all_candidates_list(request, page_size=10, page=1):
        try:
            search_term = request.data.get('search_term', '')
            filters = request.data.get('filter_data')
            filter_query = get_filters(filters)
            applied_filters = apply_filters(filter_query)
            search_term_split = search_term.split()
            search_fields = request.data.get('search_fields',[])
            if len(search_term_split) > 1:
                last_name = search_term_split[-1]
                first_name = ' '.join(search_term_split[:-1])
            applied_filters = apply_filters(filter_query)
            name_filter = f"lower(first_name) LIKE lower('%{first_name if len(search_term_split) > 1 else search_term}%') {'AND' if len(search_term_split) > 1 else 'OR'} lower(last_name) LIKE lower('%{last_name if len(search_term_split) > 1 else search_term}%')"
            search_filters = f"AND ({get_search_conditions(search_fields, search_term)} )" if len(search_fields) else f'''AND (
                (
                {name_filter}
                )
                OR (
                lower(legacy_skills) LIKE lower('%{search_term}%')
                OR lower(legacy_last_role) LIKE lower('%{search_term}%')
                OR lower(legacy_prior_roles) LIKE lower('%{search_term}%')
                OR lower(legacy_last_employer) LIKE lower('%{search_term}%')
                OR lower(legacy_prior_employers) LIKE lower('%{search_term}%')
                OR lower(city) LIKE lower('%{search_term}%')
                OR lower(phone) LIKE lower('%{search_term}%')
                OR lower(email) LIKE lower('%{search_term}%')
                OR EXISTS (
                SELECT 1
                FROM unnest(skills_resume) AS skill
                WHERE lower(skill) LIKE lower('%{search_term}%')
                )
                OR EXISTS (
                SELECT 1
                FROM candidate_candidate_skills
                INNER JOIN admin_app_skill ON candidate_candidate_skills.skill_id = admin_app_skill.id
                WHERE candidate_candidate.id = candidate_candidate_skills.candidate_id
                AND lower(admin_app_skill.tag_name) LIKE lower('%{search_term}%')
                )
                OR EXISTS (
                SELECT 1
                FROM candidate_candidate_roles
                INNER JOIN admin_app_role ON candidate_candidate_roles.role_id = admin_app_role.id
                WHERE candidate_candidate.id = candidate_candidate_roles.candidate_id
                AND lower(admin_app_role.tag_name) LIKE lower('%{search_term}%')
                )
                OR EXISTS (
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
                )
                )
                )'''
            data_query = f"""
            SELECT
            candidate_candidate.id,
            candidate_candidate.first_name,
            candidate_candidate.last_name,
            candidate_candidate.city,
            COALESCE((
            SELECT JSON_AGG(
            JSON_BUILD_OBJECT(
            'id', admin_app_role.id,
            'name', admin_app_role.tag_name
            )
            )
            FROM candidate_candidate_roles
            INNER JOIN admin_app_role ON candidate_candidate_roles.role_id = admin_app_role.id
            WHERE candidate_candidate.id = candidate_candidate_roles.candidate_id
            ), '[]') AS roles,
            COALESCE((
            SELECT JSON_AGG(
            JSON_BUILD_OBJECT(
            'id', admin_app_skill.id,
            'name', admin_app_skill.tag_name,
            'function', admin_app_skill.function_id
            )
            )
            FROM candidate_candidate_skills
            INNER JOIN admin_app_skill ON candidate_candidate_skills.skill_id = admin_app_skill.id
            WHERE candidate_candidate.id = candidate_candidate_skills.candidate_id
            ), '[]') AS skills,
            candidate_candidate.total_year_of_experience,
            candidate_candidate.years_of_break,
            candidate_candidate.flexibees_selected,
            candidate_candidate.active_projects,
            candidate_candidate.hire,
            candidate_candidate.timeline_completed,
            candidate_candidate.total_available_hours
            FROM candidate_candidate
            WHERE active=true {search_filters if search_term else ''}
            {'AND('+applied_filters+')' if applied_filters else ''}
            ORDER BY candidate_candidate.id DESC
            """
            count_query = f"""
            SELECT
            COUNT(candidate_candidate.id)
            FROM candidate_candidate
            WHERE active=true
            {search_filters if search_term else ''}
            {'AND('+applied_filters+')' if applied_filters else ''}
            """
            result = query_paginate(data_query, count_query, page=page, page_size=page_size)
            context = {
                'result':result
            }
            return Response(context)
        except Exception as e:
            log_data = [f"info|| {datetime.now()}: Exception occured in all candidates list raw query"]
            log_data.append(f"error|| {e}")
            api_logging(log_data)
            return Response(message_response(something_went_wrong))