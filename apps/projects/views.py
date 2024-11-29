from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import exceptions

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from apps.projects.models import Project, FlexiDetails, Requirement
from apps.projects.serializers import ClientDetailSerializer, FlexiDetailSerializer, \
    OtherDetailSerializer, GeneralRequirementSerializer, ProjectListSerializer, ProjectsSerializer, SalesRequirementSerializer, ContentRequirementSerializer, \
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


def stage_1_check(data, form_type):
    s1_mandatory_fields = S1_MANDATORY_FIELDS.copy()
    s1_mandatory_for_sales = S1_MANDATORY_FOR_SALES.copy()
    if form_type == 'sales':
        s1_mandatory_fields.extend(s1_mandatory_for_sales)
    # print(is_filled(data, s1_mandatory_fields))
    return is_filled(data, s1_mandatory_fields)


def stage_2_check(data, form_type):
    s2_mandatory_fields = S1_MANDATORY_FIELDS.copy() + ['no_of_positions']
    s2_mandatory_for_sales = S1_MANDATORY_FOR_SALES.copy() + ['own_contact_required', 'language']
    s2_mandatory_for_content = ['content_type', 'quantum_min', 'quantum_max', 'quantum_unit', 'word_min', 'word_max',
                                'word_unit', 'budget', 'content_duration_min', 'content_duration_max',
                                'content_duration_unit']
    if form_type == 'sales':
        s2_mandatory_fields.extend(s2_mandatory_for_sales)
    elif form_type == 'content':
        s2_mandatory_fields.extend(s2_mandatory_for_content)
    return is_filled(data, s2_mandatory_fields)



def reopen_check(project, role):
    if role == 'recruiter' and project.status == 10:
        project.status = 8
        if project.start_date is None:
            project.start_date = timezone.now()
        project.save()
    return True


class ProjectAPI(ModelViewSet):
    permission_classes = (AdminAuthentication,)
    serializer_class = ProjectUpdateSerializer

    def retrieve(self, request, pk):
        project_query = get_object_or_404(Project, id=pk, active=True)
        other = GeneralOtherDetailSerializer(project_query.otherprojectdetail_set.get_or_create()[0], partial=True)
        if project_query.form_type == 'sales':
            requirement = SalesRequirementSerializer(project_query.requirement_set.get_or_create()[0])
            other = SalesOtherDetailSerializer(project_query.otherprojectdetail_set.get_or_create()[0],
                                                partial=True)
        elif project_query.form_type == 'content':
            requirement = ContentRequirementSerializer(project_query.requirement_set.get_or_create()[0])
        else:
            requirement = GeneralRequirementSerializer(project_query.requirement_set.get_or_create()[0])
        context = {
            'client_details': ClientDetailSerializer(project_query.clientdetail_set.get_or_create()[0]).data,
            'flexi_details': FlexiDetailSerializer(project_query.flexidetails_set.get_or_create()[0],
                                                    partial=True).data,
            'other_details': other.data,
            'requirement_details': requirement.data
        }
        return Response(context)

    def update(self, request, pk):
        project_query = get_object_or_404(Project, id=pk, active=True)
        other = OtherDetailSerializer(project_query.otherprojectdetail_set.get_or_create()[0],
                                        data=request.data.get('other_details', {}), partial=True)
        if project_query.form_type == 'sales':
            requirement = SalesRequirementUpdateSerializer(project_query.requirement_set.get_or_create()[0],
                                                        data=request.data.get('requirement_details', {}), partial=True)
            other = SalesOtherDetailSerializer(project_query.otherprojectdetail_set.get_or_create()[0],
                                                data=request.data.get('other_details', {}), partial=True)
        elif project_query.form_type == 'content':
            requirement = ContentRequirementUpdateSerializer(project_query.requirement_set.get_or_create()[0],
                                                        data=request.data.get('requirement_details', {}), partial=True)
        else:
            requirement = GeneralRequirementUpdateSerializer(project_query.requirement_set.get_or_create()[0],
                                                        data=request.data.get('requirement_details', {}), partial=True)
        req_serializer = requirement
        client_serializer = ClientDetailSerializer(project_query.clientdetail_set.get_or_create()[0],
                                                    data=request.data.get('client_details', {}), partial=True)
        flexi_serializer = FlexiDetailSerializer(project_query.flexidetails_set.get_or_create()[0],
                                                    data=request.data.get('flexi_details', {}), partial=True)
        other_serializer = other
        base_serializer = ProjectBaseUpdateSerializer(project_query, data=request.data.get('requirement_details', {}),
                                                        partial=True)
        if project_query.status < 5:
            stage_1_check({**request.data.get('requirement_details', {}), **request.data.get('client_details', {}),
                           **request.data.get('flexi_details', {})}, project_query.form_type)
        else:
            stage_2_check({**request.data.get('requirement_details', {}), **request.data.get('client_details', {}),
                           **request.data.get('flexi_details', {}), **request.data.get('other_details', {})},
                            project_query.form_type)
        req_check = req_serializer.is_valid()
        flexi_check = flexi_serializer.is_valid()
        other_check = other_serializer.is_valid()
        client_check = client_serializer.is_valid()
        base_check = base_serializer.is_valid()
        if req_check and flexi_check and client_check and other_check and base_check:
            req_serializer.save()
            client_serializer.save()
            flexi_serializer.save()
            other_serializer.save()
            base_serializer.save()
            if project_query.status == 1 and stage_1_check({**req_serializer.data, **client_serializer.data,
                                                            **flexi_serializer.data, **base_serializer.data},
                                                            project_query.form_type):
                project_query.status = 2
                project_query.save()
            elif project_query.status == 5 and stage_2_check({**req_serializer.data, **client_serializer.data,
                                                              **flexi_serializer.data, **other_serializer.data,
                                                              **base_serializer.data},
                                                                project_query.form_type):
                project_query.status = 6
                project_query.save()

            return self.retrieve(request, pk)
        return Response(message_response(mandatory_fields_missing), status=400)

    def view_project(self, request, project):
        project_query = get_object_or_404(Project, id=project, active=True)
        other = OtherDetailsListSerializer(project_query.otherprojectdetail_set.get_or_create()[0], partial=True)
        if project_query.form_type == 'sales':
            requirement = SalesRequirementSerializer(project_query.requirement_set.get_or_create()[0])
            other = SalesOtherDetailSerializer(project_query.otherprojectdetail_set.get_or_create()[0],
                                                partial=True)
        elif project_query.form_type == 'content':
            requirement = ContentRequirementSerializer(project_query.requirement_set.get_or_create()[0])
        else:
            requirement = GeneralRequirementSerializer(project_query.requirement_set.get_or_create()[0])
        context = {
            'client_details': ClientDetailsSerializer(project_query.clientdetail_set.get_or_create()[0]).data,
            'flexi_details': FlexiDetailsSerializer(project_query.flexidetails_set.get_or_create()[0], partial=True).data,
            'other_details': other.data,
            'requirement_details': requirement.data
        }
        return Response(context)

    def recruiter_project_update(self, request, project):
        project_query = get_object_or_404(Project, id=project, active=True)
        other = OtherDetailSerializer(project_query.otherprojectdetail_set.get_or_create()[0],
                                        data=request.data.get('other_details', {}), partial=True)
        if project_query.form_type == 'sales':
            requirement = SalesRequirementUpdateSerializer(project_query.requirement_set.get_or_create()[0],
                                                        data=request.data.get('requirement_details', {}), partial=True)
            other = SalesOtherDetailSerializer(project_query.otherprojectdetail_set.get_or_create()[0],
                                                data=request.data.get('other_details', {}), partial=True)
        elif project_query.form_type == 'content':
            requirement = ContentRequirementUpdateSerializer(project_query.requirement_set.get_or_create()[0],
                                                        data=request.data.get('requirement_details', {}), partial=True)
        else:
            requirement = GeneralRequirementUpdateSerializer(project_query.requirement_set.get_or_create()[0],
                                                        data=request.data.get('requirement_details', {}), partial=True)
        req_serializer = requirement
        client_serializer = ClientDetailSerializer(project_query.clientdetail_set.get_or_create()[0],
                                                    data=request.data.get('client_details', {}), partial=True)
        flexi_serializer = FlexiDetailSerializer(project_query.flexidetails_set.get_or_create()[0],
                                                    data=request.data.get('flexi_details', {}), partial=True)
        other_serializer = other
        base_serializer = ProjectBaseUpdateSerializer(project_query, data=request.data.get('requirement_details', {}),
                                                        partial=True)
        if project_query.status < 5:
            stage_1_check({**request.data.get('requirement_details', {}), **request.data.get('client_details', {}),
                           **request.data.get('flexi_details', {})}, project_query.form_type)
        else:
            stage_2_check({**request.data.get('requirement_details', {}), **request.data.get('client_details', {}),
                           **request.data.get('flexi_details', {}), **request.data.get('other_details', {})},
                            project_query.form_type)
        req_check = req_serializer.is_valid()
        flexi_check = flexi_serializer.is_valid()
        other_check = other_serializer.is_valid()
        client_check = client_serializer.is_valid()
        base_check = base_serializer.is_valid()
        if req_check and flexi_check and client_check and other_check and base_check:
            req_serializer.save()
            client_serializer.save()
            flexi_serializer.save()
            other_serializer.save()
            base_serializer.save()
            return self.retrieve(request, project)
        return Response(message_response(mandatory_fields_missing), status=400)
    
    

class AllProjectCountAPI(ModelViewSet):
    # permission_classes = (AdminAuthentication,)

    @staticmethod
    def all_project_count(request):
        all_projects = Project.objects.filter(active=True)
        context = {
            'from_crm': all_projects.filter(status__in=[1, 2]).count(),
            'profile_table': all_projects.filter(status__in=[3, 4, 5]).count(),
            'recruitment': all_projects.filter(status__in=[7, 8]).count(),
            'final_selection': 0,
            'closed': 0,
            'suspended': 0
        }
        return Response(context)


class ProjectInfoAPI(ModelViewSet):
    permission_classes = (AdminAuthentication,)

    def project_info(self, request, project):
        requirement_obj = Requirement.objects.get_or_create(project=project, active=True)[0]
        serializer = ProjectInfoSerializer(requirement_obj)
        return Response(serializer.data)

class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectsSerializer

