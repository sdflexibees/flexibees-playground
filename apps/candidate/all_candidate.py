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


class CandidateAPI(ModelViewSet):
    permission_classes = (AdminAuthentication,)
    serializer_class = SearchListSerializer

    def project_all_candidate_list(self, request, project, page_size=10, page=1):
        project_query = get_object_or_404(Project, id=project, active=True)
        flexi_data = project_query.flexidetails_set.get_or_create()[0]
        reopen_check(project_query, request.role)
        role = str(project_query.role.id)
        must_have_skills = list(project_query.requirement_set.get_or_create()[0].must_have_skills.
                                values_list('id', flat=True))
        search_term = request.data.get('search_term', '')
        filters = request.data.get('filter_data')
        filter_query = {}
        shortlist_candidate_ids = list(Shortlist.objects.filter(project=project).values_list('candidate', flat=True))
        all_candidates = Candidate.objects.filter(active=True, hire=True).exclude(id__in=shortlist_candidate_ids)
        if filters:
            filter_query.update({'skills__in': filters.get('skills')}) if len(filters.get('skills', [])) != 0 \
                else filter_query
            filter_query.update({'roles__in': filters.get('roles')}) if len(filters.get('roles', [])) != 0 \
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
            if filters.get('relevant_experience'):
                relevant_experience = filters.get('relevant_experience')
                if relevant_experience.get('min') and relevant_experience.get('min') != "":
                    filter_query.update({'relevantexp__r' + role + '__gte': relevant_experience.get('min')})
                if relevant_experience.get('max') and relevant_experience.get('max') != "":
                    filter_query.update({'relevantexp__r' + role + '__lte': relevant_experience.get('max')})
        matching = matching_candidates(filter_query, all_candidates, must_have_skills, search_term,
                                       city=flexi_data.selected_city,
                                       min_working_hours=flexi_data.min_no_of_working_hours,
                                       is_travel_required=flexi_data.is_travel_required)
        search_filter = get_search_filters(search_term)
        candidates_query = all_candidates.filter(search_filter[0] | search_filter[1], **filter_query)
        if matching['matching_ids']:
            matching_ids = matching['matching_ids']
            partial_matching_ids = matching['any_matching_ids']
            matching_query = candidates_query.filter(id__in=matching_ids).prefetch_related('skills', 'roles').distinct().order_by('-id')
            partial_matching_query = candidates_query.filter(id__in=partial_matching_ids).prefetch_related('skills', 'roles').distinct().order_by('-id')
            non_matching_query = candidates_query.exclude(id__in=matching_ids+partial_matching_ids).prefetch_related('skills', 'roles').distinct().order_by('-id')
            candidates_query = list(matching_query) + list(partial_matching_query) + list(non_matching_query)
        elif matching['any_matching_ids']:
            partial_matching_ids = matching['any_matching_ids']
            partial_matching_query = candidates_query.filter(id__in=partial_matching_ids).prefetch_related('skills','roles').distinct().order_by('-id')
            non_matching_query = candidates_query.exclude(id__in=partial_matching_ids).prefetch_related('skills', 'roles').distinct().order_by('-id')
            candidates_query = list(partial_matching_query) + list(non_matching_query)
        else:
            candidates_query = candidates_query.prefetch_related('skills', 'roles').distinct().order_by('-id')
        result = paginate(candidates_query, AllCandidateListSerializer, page=page, page_size=page_size,
                          context={
                              'must_have_skills': must_have_skills,
                              'project_role': role,
                              'project': project,
                              'min_no_of_working_hours': flexi_data.min_no_of_working_hours,
                              'max_no_of_working_hours': flexi_data.max_no_of_working_hours,
                              'willing_to_travel': flexi_data.is_travel_required,
                              'city': flexi_data.selected_city
                          }
                          )
        context = {
            'result': result,
            'filter_data': {
                'skills': list(Skill.objects.filter(function=project_query.function, active=True).
                               values('id', 'tag_name').distinct().order_by('tag_name')),
                'roles': list(Role.objects.filter(active=True).
                              values('id', 'tag_name').distinct().order_by('tag_name')),
                'active_projects': list(
                    all_candidates.values_list('active_projects', flat=True).distinct().order_by(
                        'active_projects')),
                'total_available_hours': list(
                    all_candidates.filter(timeline_completed=True).values_list(
                        'total_available_hours', flat=True).distinct().order_by('total_available_hours')),
                'flexibees_selected': list(
                    all_candidates.values_list('flexibees_selected', flat=True).distinct().order_by('flexibees_selected'))
            }
        }
        return Response(context)


    @staticmethod
    def all_candidates_list(request, page_size=10, page=1):
        search_term = request.data.get('search_term', '')
        filters = request.data.get('filter_data')
        filter_query = {}
        if filters:
            filter_query.update({'city__in': filters.get('cities')}) if len(filters.get('cities', [])) != 0 \
                else filter_query
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
            filter_query.update({'years_of_break__in': filters.get('years_of_break')}) if len(
                filters.get('years_of_break', [])) != 0 else filter_query
        all_candidates = Candidate.objects.filter(active=True).order_by('-id')
        search_filter = get_search_filters(search_term)
        candidate_query = all_candidates.filter(search_filter[0] | search_filter[1], **filter_query).\
            prefetch_related('skills', 'roles').distinct()
        result = paginate(candidate_query, AllCandidateListingSerializer, page=page, page_size=page_size)
        context = {
            'result': result,
            'filter_data': {
                'skills': list(Skill.objects.filter(active=True).
                               values('id', 'tag_name').distinct().order_by('tag_name')),
                'roles': list(Role.objects.filter(active=True).
                              values('id', 'tag_name').distinct().order_by('tag_name')),
                'cities': list(all_candidates.values_list('city', flat=True).distinct()),
                'years_of_experience': list(
                    all_candidates.values_list('total_year_of_experience', flat=True).distinct(
                    ).order_by('total_year_of_experience')),
                'years_of_break': list(
                    all_candidates.values_list('years_of_break', flat=True).distinct().order_by(
                        'years_of_break')),
                'active_projects': list(
                    all_candidates.values_list('active_projects', flat=True).distinct().order_by(
                        'active_projects')),
                'total_available_hours': list(
                    all_candidates.filter(timeline_completed=True).values_list(
                        'total_available_hours', flat=True).distinct().order_by('total_available_hours')),
                'flexibees_selected': list(all_candidates.values_list(
                    'flexibees_selected', flat=True).distinct().order_by('flexibees_selected'))
            }
        }
        return Response(context)

    @staticmethod
    def candidate_city_list(request, page_size=10, page=1):
        search_term = request.data.get('search_term', '')
        cities_query = Candidate.objects.filter(active=True, city__icontains=search_term).distinct('city')
        result = paginate(cities_query, AllCandidateCitySerializer, page=page, page_size=page_size)
        return Response({'result': result})
    
    @staticmethod
    def all_candidate_list_filters(request):
        all_candidates = Candidate.objects.filter(active=True).values('city', 'total_year_of_experience', 'years_of_break', 'active_projects','flexibees_selected').order_by('-id')
        data={
            'cities':[],
            'years_of_experience':[],
            'years_of_break':[],
            'active_projects':[],
            'flexibees_selected':[],
        }
        for candidate in all_candidates:
            data['cities'].append(candidate['city'])
            data['years_of_experience'].append(candidate['total_year_of_experience'])
            data['years_of_break'].append(candidate['years_of_break'])
            data['active_projects'].append(candidate['active_projects'])
            data['flexibees_selected'].append(candidate['flexibees_selected'])
        context = {
            'skills': list(Skill.objects.filter(active=True).
                            values('id', 'tag_name').distinct().order_by('tag_name')),
            'roles': list(Role.objects.filter(active=True).
                            values('id', 'tag_name').distinct().order_by('tag_name')),
            'cities': sorted(list(set(data['cities'])), key=lambda x: x),
            'years_of_experience': sorted(list(set(data['years_of_experience'])), key=lambda x: x),
            'years_of_break': sorted(list(set(data['years_of_break'])), key=lambda x: x),
            'active_projects': sorted(list(set(data['active_projects'])), key=lambda x: x),
            'total_available_hours': list(
                Candidate.objects.filter(active=True).order_by('-id').filter(timeline_completed=True).values_list(
                    'total_available_hours', flat=True).distinct().order_by('total_available_hours')),
            'flexibees_selected': sorted(list(set(data['flexibees_selected'])), key=lambda x: x),
            }
        return Response(context)

    @staticmethod
    def project_all_candidate_list_filters(request, project):
        project_query = get_object_or_404(Project, id=project, active=True)
        shortlist_candidate_ids = list(Shortlist.objects.filter(project=project).values_list('candidate', flat=True))
        all_candidates = Candidate.objects.filter(active=True, hire=True).exclude(id__in=shortlist_candidate_ids)
        all_candidates_data = all_candidates.values('active_projects','flexibees_selected')
        data={
            'active_projects':[],
            'flexibees_selected':[],
        }
        for candidate in all_candidates_data:
            data['active_projects'].append(candidate['active_projects'])
            data['flexibees_selected'].append(candidate['flexibees_selected'])
        context =  {
            'skills': list(Skill.objects.filter(function=project_query.function, active=True).
                            values('id', 'tag_name').distinct().order_by('tag_name')),
            'roles': list(Role.objects.filter(active=True).
                            values('id', 'tag_name').distinct().order_by('tag_name')),
            'active_projects': sorted(list(set(data['active_projects'])), key=lambda x: x),
            'total_available_hours': list(
                all_candidates.filter(timeline_completed=True).values_list(
                    'total_available_hours', flat=True).distinct().order_by('total_available_hours')),
            'flexibees_selected': sorted(list(set(data['flexibees_selected'])), key=lambda x: x),
            }
        return Response(context)

class CandidateListAPI(ModelViewSet):
    permission_classes = (AdminAuthentication,)
    serializer_class = SearchListSerializer

    def project_all_candidate_list(self, request, project, page_size=10, page=1):
        project_query = get_object_or_404(Project, id=project, active=True)
        try:
            reopen_check(project_query, request.role)
            flexi_data = project_query.flexidetails_set.get_or_create()[0]
            role = str(project_query.role.id)
            must_have_skills = list(project_query.requirement_set.get_or_create()[0].must_have_skills.
                                    values_list('id', flat=True))
            search_term = request.data.get('search_term', '')
            filters = request.data.get('filter_data')
            filter_query = get_filters(filters, role)
            matching = [
                ('total_available_hours__gte', flexi_data.min_no_of_working_hours),
                ('skills__id__in', must_have_skills)
            ]
            if flexi_data.is_travel_required and flexi_data.selected_city != '':
                matching.append(('city__iexact', flexi_data.selected_city))
            matching_filter = reduce(operator.and_, [Q((x[0], x[1])) for x in matching])
            search_query = Q()
            if search_term:
                search_filter = get_search_filters(search_term)
                search_query |= Q(search_filter[0])
                search_query |= Q(search_filter[1])
            candidates_query = Candidate.objects.filter(active=True, hire=True,**filter_query).\
                filter(search_query).\
                        exclude(shortlist__project__id=project).order_by(
                            Case(
                                When(matching_filter, then=Value(0)),
                                When(skills__id__in=must_have_skills, then=Value(1)),
                                default=Value(2),
                                output_field=IntegerField()
                            ),
                            '-id'
                        ).distinct()
            result = paginate(candidates_query, AllCandidateListSerializer, page=page, page_size=page_size,
                            context={
                                'must_have_skills': must_have_skills,
                                'project_role': role,
                                'project': project,
                                'min_no_of_working_hours': flexi_data.min_no_of_working_hours,
                                'max_no_of_working_hours': flexi_data.max_no_of_working_hours,
                                'willing_to_travel': flexi_data.is_travel_required,
                                'city': flexi_data.selected_city
                            }
                            )
            context = {
                'result': result,
            }
            return Response(context)
        except Exception as e:
            log_data = [f"info|| {datetime.now()}: Exception occured in project all candidates list"]
            log_data.append(f"error|| {e}")
            api_logging(log_data)
            return Response(message_response(something_went_wrong))
        
    @staticmethod
    def all_candidates_list(request, page_size=10, page=1):
        try:
            search_term = request.data.get('search_term', '')
            filters = request.data.get('filter_data')
            filter_query = get_filters(filters)
            search_query = Q()
            if search_term:
                search_filter = get_search_filters(search_term)
                search_query |= Q(search_filter[0])
                search_query |= Q(search_filter[1])
            candidate_query = Candidate.objects.filter(active=True).filter(search_query, **filter_query).distinct().order_by('-id')
            result = paginate(candidate_query, AllCandidateListingSerializer, page=page, page_size=page_size)
            context = {
                'result': result,
            }
            return Response(context)
        except Exception as e:
            log_data = [f"info|| {datetime.now()}: Exception occured in all candidates list"]
            log_data.append(f"error|| {e}")
            api_logging(log_data)
            return Response(message_response(something_went_wrong))

class CandidateList(ModelViewSet):
    permission_classes = (AdminAuthentication,)
    serializer_class = SearchListSerializer

    @staticmethod
    @api_exception_handler(api_name=PROJECT_ALL_CADNDIDATES_LIST)
    def project_all_candidate_list(request, project, page_size=10, page=1):
        project_query = get_object_or_404(Project, id=project, active=True)
        flexi_data = project_query.flexidetails_set.get_or_create()[0]
        reopen_check(project_query, request.role)
        role = str(project_query.role.id)
        must_have_skills_objs = project_query.requirement_set.get_or_create()[0].must_have_skills.all()

        must_have_skills, must_have_skills_name = [], []
        for skill in must_have_skills_objs:
            must_have_skills.append(skill.id)
            must_have_skills_name.append(skill.tag_name)
        search_term = request.data.get('search_term', '')
        filters = request.data.get('filter_data')
        matching = filters.get('matching', False)
        search_fields = request.data.get('search_fields',[])

        filter_query = get_filters(filters, role)
        applied_filters = apply_filters(filter_query, role)
        search_term_split = search_term.split()
        # Load the weightage configuration from a JSON file
        with open('weights.json', 'r') as file:
            weightage = json.load(file)
        if len(search_term_split) > 1:
            last_name = search_term_split[-1]
            first_name = ' '.join(search_term_split[:-1])
        # project required hours 
        flexi_details = FlexiDetails.objects.filter(project__id=project_query.id).first()
        hours, unit = None, None
        if flexi_details:
            hours = flexi_details.min_no_of_working_hours
            unit = flexi_details.working_hours_duration_unit.lower()
        min_years_of_exp = 0
        # get minimum experience 
        requirement_details = Requirement.objects.filter(project__id=project_query.id).first()
        if requirement_details:
            min_years_of_exp = requirement_details.min_total_experience_needed

        project_hours = get_project_required_hours(hours, unit)
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
        # name filter 
        name_filter = f"lower(first_name) LIKE lower('%{first_name if len(search_term_split) > 1 else search_term}%') {'AND' if len(search_term_split) > 1 else 'OR'} lower(last_name) LIKE lower('%{last_name if len(search_term_split) > 1 else search_term}%')"
        # search filters 
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
            WHERE candidate_candidate.id = candidate_employmentdetail.candidate_id AND candidate_employmentdetail.active=true
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
        # creterias to calcuate the matching percentage 
        matching_algo = f"""
            CEIL((
                (
                    -- Skill match
                    (
                        SELECT COUNT(*)
                        FROM candidate_candidate_skills
                        WHERE candidate_candidate.id = candidate_candidate_skills.candidate_id
                        AND candidate_candidate_skills.skill_id IN ({", ".join(str(item) for item in must_have_skills)})
                    ) * {weightage['skills']} / NULLIF({len(must_have_skills)}, 0)  -- Weight for skill match
                    
                    + (
                        -- Role match
                        CASE
                            WHEN EXISTS (
                                SELECT 1
                                FROM candidate_employmentdetail
                                WHERE candidate_id = candidate_candidate.id AND role_id={project_query.role.id}  AND active=true
                            )
                            THEN {weightage['role']}
                            ELSE 0
                        END
                    )

                    + (
                        -- Total experience calculation
                        CASE
                            WHEN (
                                SELECT SUM(EXTRACT(YEAR FROM age(end_date, start_date)))
                                FROM candidate_employmentdetail
                                WHERE candidate_id = candidate_candidate.id AND role_id = {project_query.role.id} AND candidate_employmentdetail.active=true
                            ) >= {min_years_of_exp}
                            THEN {weightage['experience']}
                            ELSE 0
                        END
                    )
                    
                    + (
                        -- Recency match
                        CASE
                            WHEN candidate_candidate.last_login >= NOW() - INTERVAL '90 DAY'
                            THEN {weightage['recency']}
                            ELSE 0
                        END
                    )
                    
                    + (
                        -- Domain match
                        CASE
                            WHEN EXISTS (
                                SELECT 1
                                FROM candidate_employmentdetail
                                INNER JOIN admin_app_domain ON admin_app_domain.tag_name = '{project_query.function.tag_name}'
                                WHERE candidate_employmentdetail.candidate_id = candidate_candidate.id AND candidate_employmentdetail.active=true
                            )
                            THEN {weightage['domain']}
                            ELSE 0
                        END
                    )
                    
                    + 
                        -- Availability match
                        CASE
                            WHEN {project_hours} = 0 
                            THEN {weightage['total_available_hours']}  -- Full weightage if project_hours is zero
                            WHEN candidate_candidate.total_available_hours > 0 
                            THEN LEAST((candidate_candidate.total_available_hours / {project_hours}) * {weightage['total_available_hours']}, {weightage['total_available_hours']})
                            ELSE 0  -- No weightage if total_available_hours is 0
                        END
            
                    + (
                        COALESCE((
                            SELECT AVG(COALESCE((feedback->>'rating')::int, 0))
                            FROM candidate_functionalfeedback
                            CROSS JOIN LATERAL jsonb_array_elements(candidate_functionalfeedback.skills_feedback) AS feedback
                            INNER JOIN candidate_functional 
                                ON candidate_functional.id = candidate_functionalfeedback.functional_id 
                                AND candidate_functional.candidate_id = candidate_candidate.id
                            WHERE (feedback->>'skill') IN ({", ".join(f"'{str(item)}'" for item in must_have_skills_name)})
                        ), 0) / {MAX_RATING}) * {weightage['functional_interview']}
                        )/{sum(weightage.values())} * 100)  -- Convert to percentage
                    ) AS match_percentage
        """
        min_percentage, max_percentage = None, None
        match_filter = filters.get('match')
        if match_filter:
            min_percentage = match_filter.get('min')
            max_percentage = match_filter.get('max')
        # matching percentage filter 
        matching_filter = ''
        if min_percentage and max_percentage:
            matching_filter = f"WHERE match_percentage >= {min_percentage} AND match_percentage <= {max_percentage}"
        elif min_percentage:
            matching_filter = f"WHERE match_percentage >= {min_percentage}"
        elif max_percentage:
            matching_filter = f"WHERE match_percentage <= {max_percentage}"
        # final query to fetch the data 
        data_query = f"""
            WITH candidate_data AS (
            SELECT
                candidate_candidate.id,
                candidate_candidate.first_name,
                candidate_candidate.city AS Candidate_city,
                candidate_candidate.total_year_of_experience,
                candidate_candidate.flexibees_selected,
                candidate_candidate.active_projects,
                candidate_candidate.hire,
                candidate_candidate.timeline_completed,
                candidate_candidate.total_available_hours,
                candidate_candidate.legacy_skills,
                TO_CHAR(candidate_candidate.last_login, 'YYYY-MM-DD HH24:MI:SS') AS last_login,
                candidate_candidate.skills_resume,
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
                    AND candidate_candidate.total_available_hours >= {flexi_data.min_no_of_working_hours} 
                    THEN true
                    ELSE false
                END AS must_have_skills,
                CASE
                    WHEN candidate_candidate.total_available_hours >= {flexi_data.min_no_of_working_hours} THEN 'green'
                    ELSE 'red'
                END AS availability,
                {matching_algo}
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
                        match_percentage DESC,
                        candidate_candidate.id DESC  -- Order by candidate ID as a tiebreaker
                    {f'OFFSET {(page - 1) * page_size} LIMIT {page_size}'}
                    )
                    SELECT *
                    FROM candidate_data 
                    {matching_filter}
                    ORDER BY
                        match_percentage DESC
                    """
        # Final query with conditional matching logic
        count_query = f"""
            WITH candidate_data AS (
                SELECT 
                    candidate_candidate.id
                    {f", {matching_algo}" if min_percentage or max_percentage else ''}
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
            )
            SELECT COUNT(*)
            FROM candidate_data
            {matching_filter}
        """
        # paginate the response 
        result = query_paginate(data_query, count_query, page=page, page_size=page_size, paginate=False)
        [x.update({'match': x.get('match_percentage')}) for x in result['results']]
        context = {
            'result':result
        }
        return Response(context)
    
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
                WHERE candidate_candidate.id = candidate_employmentdetail.candidate_id AND candidate_employmentdetail.active=true
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