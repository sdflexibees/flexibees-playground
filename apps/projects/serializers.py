import numpy as np
from django.utils import timezone
from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField, DateTimeField, IntegerField, \
    Serializer, DictField

from apps.admin_app.serializers import FunctionSerializer, RoleSerializer, SkillSerializer, DomainSerializer, \
    AdminInfoSerializer
from apps.projects.models import Project, Requirement, FlexiDetails, OtherProjectDetail, ClientDetail, Pricing, \
    Suspended, Closed, Reopen

default_blank = {'default': ''}


def working_days(start_date):
    if start_date:
        today = timezone.now().date()
        return np.busday_count(start_date.date(), today)
    return 0


class CRMListSerializer(ModelSerializer):
    function = FunctionSerializer()
    role = RoleSerializer()
    proposed_date = SerializerMethodField('fetch_proposed_date')

    @staticmethod
    def fetch_proposed_date(instance):
        return instance.created.strftime("%d/%m/%Y")

    class Meta:
        model = Project
        fields = ('id', 'deal_name', 'zoho_id', 'bd_email','bd', 'company_name', 'contact_name', 'function', 'role',
                  'role_type', 'model_type', 'description', 'flex_details', 'stage', 'status_description', 'next_step',
                  'post_status', 'project_created', 'form_type', 'status', 'proposed_date', )


class ClientDetailSerializer(ModelSerializer):

    class Meta:
        model = ClientDetail
        fields = ('company_website', 'company_brief', 'currency',)


class FlexiDetailSerializer(ModelSerializer):

    class Meta:
        model = FlexiDetails
        fields = ('location_constraints', 'selected_city', 'is_travel_required', 'how_often_travelling',
                  'company_address', 'min_no_of_working_hours', 'max_no_of_working_hours', 'working_hours_duration_unit',
                  'project_duration', 'project_duration_unit', 'turn_around_time', 'turn_around_duration_unit',
                  'client_assignment', 'assignment_file', 'assignment_duration', 'selected_country',
                  'type_of_payout')


class FlexiDetailsSerializer(ModelSerializer):

    class Meta:
        model = FlexiDetails
        fields = ('location_constraints', 'selected_city', 'is_travel_required', 'how_often_travelling',
                  'company_address', )


class OtherDetailSerializer(ModelSerializer):

    class Meta:
        model = OtherProjectDetail
        fields = ('compensation_from_client', 'travel_expense_reimbursement', 'phone_reimbursement',
                  'other_comments')


class PricingDetailsSerializer(ModelSerializer):

    class Meta:
        model = Pricing
        fields = ('type_of_payout', 'min_salary', 'max_salary', 'project_duration', 'project_duration_unit',
                  'comments')


class GeneralRequirementSerializer(ModelSerializer):
    function = FunctionSerializer(source='project.function', required=False)
    role = RoleSerializer(source='project.role', required=False)
    role_type = CharField(source='project.role_type')
    model_type = CharField(source='project.model_type')
    must_have_skills = SkillSerializer(many=True)
    nice_to_have_skills = SkillSerializer(many=True)
    must_have_domains = DomainSerializer(many=True)
    nice_to_have_domain = DomainSerializer(many=True)
    salary_details = SerializerMethodField('fetch_salary_details')

    @staticmethod
    def fetch_salary_details(instance):
        pricing_obj = Pricing.objects.filter(project=instance.project, active=True).order_by('-id')
        if pricing_obj.exists():
            return PricingDetailsSerializer(pricing_obj[0]).data
        else:
            return {
                'type_of_payout': instance.project.flexidetails_set.get_or_create()[0].type_of_payout,
                'min_salary': '',
                'max_salary': '',
                'project_duration': instance.project.flexidetails_set.get_or_create()[0].project_duration,
                'project_duration_unit': instance.project.flexidetails_set.get_or_create()[0].project_duration_unit,
                'comments': ''
            }

    class Meta:
        model = Requirement
        fields = ('no_of_positions', 'min_total_experience_needed', 'max_total_experience_needed',
                  'min_relevant_experience', 'max_relevant_experience', 'educational_constraints', 'education',
                  'must_have_skills', 'nice_to_have_skills', 'must_have_domains', 'nice_to_have_domain',
                  'function', 'role', 'role_type', 'model_type', 'detailed_job_description', 'salary_details', )


class SalesRequirementSerializer(GeneralRequirementSerializer):

    class Meta:
        model = Requirement
        fields = GeneralRequirementSerializer.Meta.fields + ('sale_type', 'describe_more',
                                                             'lead_generation_requirement', 'own_contact_required',
                                                             'if_yes', 'lead_expresses_interest', 'language',
                                                             'communication_skill_level', 'target_audience')


class ContentRequirementSerializer(GeneralRequirementSerializer):

    class Meta:
        model = Requirement
        fields = GeneralRequirementSerializer.Meta.fields + ('target_audience', 'goals', 'content_type', 'quantum_min',
                                                             'quantum_max', 'quantum_unit', 'word_min', 'word_max',
                                                             'word_unit', 'sample_work', 'sample_work_detail',
                                                             'budget', 'content_duration_min', 'content_duration_max',
                                                             'content_duration_unit')


class GeneralRequirementUpdateSerializer(ModelSerializer):

    class Meta:
        model = Requirement
        fields = ('no_of_positions', 'min_total_experience_needed', 'max_total_experience_needed',
                  'min_relevant_experience', 'max_relevant_experience', 'educational_constraints', 'education',
                  'must_have_skills', 'nice_to_have_skills', 'must_have_domains', 'nice_to_have_domain',
                  'detailed_job_description')


class SalesRequirementUpdateSerializer(GeneralRequirementUpdateSerializer):

    class Meta:
        model = Requirement
        fields = GeneralRequirementUpdateSerializer.Meta.fields + ('sale_type', 'describe_more',
                                                             'lead_generation_requirement', 'own_contact_required',
                                                             'if_yes', 'lead_expresses_interest', 'language',
                                                             'communication_skill_level', 'target_audience')


class ContentRequirementUpdateSerializer(GeneralRequirementUpdateSerializer):

    class Meta:
        model = Requirement
        fields = GeneralRequirementUpdateSerializer.Meta.fields + ('target_audience', 'goals', 'content_type', 'quantum_min',
                                                             'quantum_max', 'quantum_unit', 'word_min', 'word_max',
                                                             'word_unit', 'sample_work', 'sample_work_detail',
                                                             'budget', 'content_duration_min', 'content_duration_max',
                                                             'content_duration_unit')


class CRMSerializer(ModelSerializer):

    class Meta:
        model = Project
        exclude = ('modified', 'active',)
        read_only_fields = ('id',)


class RequirementsListSerializer(ModelSerializer):
    must_have_skills = SkillSerializer(many=True)
    nice_to_have_skills = SkillSerializer(many=True)
    must_have_domains = DomainSerializer()
    nice_to_have_domain = DomainSerializer()

    class Meta:
        model = Requirement
        exclude = ('modified', 'active',)
        read_only_fields = ('id',)


class FlexiDetailsListSerializer(ModelSerializer):

    class Meta:
        model = FlexiDetails
        exclude = ('modified', 'active',)
        read_only_fields = ('id',)


class OtherProjectDetailsListSerializer(ModelSerializer):

    class Meta:
        model = OtherProjectDetail
        exclude = ('modified', 'active',)
        read_only_fields = ('id',)


class GeneralOtherDetailSerializer(ModelSerializer):
    class Meta:
        model = OtherProjectDetail
        fields = ('travel_expense_reimbursement', 'phone_reimbursement', 'other_comments', 'compensation_from_client',)
        read_only_fields = ('id',)


class SalesOtherDetailSerializer(ModelSerializer):
    class Meta:
        model = OtherProjectDetail
        fields = ('client_variable', 'compensation_structure', 'when_make_it_known', 'existing_team',
                  'travel_expense_reimbursement', 'phone_reimbursement', 'other_comments',)
        read_only_fields = ('id',)


class ProfileTableListSerializer(ModelSerializer):
    function = CharField(source='function.tag_name')
    role = CharField(source='role.tag_name')
    request_date = SerializerMethodField('fetch_request_date')

    @staticmethod
    def fetch_request_date(instance):
        if instance.request_date:
            return instance.request_date.strftime("%d/%m/%Y")

    class Meta:
        model = Project
        fields = ('id', 'company_name', 'function', 'role', 'status', 'request_date', )


class RecruiterAdminProfileTableListSerializer(ProfileTableListSerializer):
    proposed_date = SerializerMethodField('fetch_proposed_date')
    bd = AdminInfoSerializer()
    status = SerializerMethodField('fetch_status')

    @staticmethod
    def fetch_proposed_date(instance):
        if instance.request_date:
            return instance.request_date.strftime("%d/%m/%Y")

    @staticmethod
    def fetch_status(instance):
        status = instance.status
        if status in [5, 6]:
            status = 4
        return status

    class Meta:
        model = Project
        fields = ('id', 'company_name', 'function', 'role', 'status', 'proposed_date', 'bd', )


class RecruitmentListSerializer(ModelSerializer):
    function = FunctionSerializer()
    role = RoleSerializer()
    start_date = SerializerMethodField('fetch_start_date')
    sent_to_recruitment_date = SerializerMethodField('fetch_date_sent_to_recruitment')
    assigned_to_recruiter_date = SerializerMethodField('fetch_date_assigned_to_recruiter')
    sent_to_profile_table_date = SerializerMethodField('fetch_date_sent_to_profile_table')
    date_sent_final_client_pricing = SerializerMethodField('fetch_date_sent_final_client_pricing')
    no_of_days = IntegerField(source='recruitment_days')
    recruiter = AdminInfoSerializer()

    @staticmethod
    def fetch_working_days(instance):
        return working_days(instance.start_date)

    @staticmethod
    def fetch_start_date(instance):
        if instance.start_date:
            return instance.start_date.strftime("%d/%m/%Y")
        return None
    
    @staticmethod
    def fetch_date_sent_to_recruitment(instance):
        if instance.date_sent_to_recruitment:
            return instance.date_sent_to_recruitment.strftime("%d/%m/%Y")
        return None
    
    @staticmethod
    def fetch_date_assigned_to_recruiter(instance):
        if instance.date_assigned_to_recruiter:
            return instance.date_assigned_to_recruiter.strftime("%d/%m/%Y")
        return None
    
    @staticmethod
    def fetch_date_sent_to_profile_table(instance):
        if instance.request_date:
            return instance.request_date.strftime("%d/%m/%Y")
        return None
    
    @staticmethod
    def fetch_date_sent_final_client_pricing(instance):
        pricing = instance.pricing_set.filter(stage=Pricing.STAGE_CHOICES[2][0]).first()
        if pricing:
            return pricing.created.strftime("%d/%m/%Y")
        return None
    class Meta:
        model = Project
        fields = ('id', 'company_name', 'function', 'role', 'start_date', 'recruiter', 'status', 'no_of_days', 'sent_to_recruitment_date', 'assigned_to_recruiter_date', 'sent_to_profile_table_date', 'date_sent_final_client_pricing')


class RecruiterAdminRecruitmentListSerializer(RecruitmentListSerializer):
    bd = AdminInfoSerializer()

    class Meta:
        model = Project
        fields = RecruitmentListSerializer.Meta.fields + ('bd', )


class RecruiterRecruitmentListSerializer(RecruitmentListSerializer):
    bd = AdminInfoSerializer()

    class Meta:
        model = Project
        fields = ('id', 'company_name', 'function', 'role', 'start_date', 'bd', 'status', 'no_of_days', )


class PricingSerializer(ModelSerializer):

    class Meta:
        model = Pricing
        exclude = ('modified', 'active',)
        read_only_fields = ('id',)


class FinalSelectionListSerializer(ModelSerializer):
    function = CharField(source='function.tag_name')
    role = CharField(source='role.tag_name')
    start_date = SerializerMethodField('fetch_start_date')
    recruiter = AdminInfoSerializer()
    no_of_days = IntegerField(source='recruitment_days')
    positions_to_be_filled = SerializerMethodField('fetch_no_of_positions')

    @staticmethod
    def fetch_working_days(instance):
        return working_days(instance.start_date)

    @staticmethod
    def fetch_no_of_positions(instance):
        return instance.requirement_set.get_or_create()[0].no_of_positions

    @staticmethod
    def fetch_start_date(instance):
        if instance.start_date:
            return instance.start_date.strftime("%d/%m/%Y")
        return None

    class Meta:
        model = Project
        fields = ('id', 'company_name', 'function', 'role', 'start_date', 'recruiter', 'no_of_days',
                  'positions_to_be_filled', 'flexibees_selected', 'client_selected', )


class RecruiterAdminFinalSelectionListSerializer(FinalSelectionListSerializer):
    bd = AdminInfoSerializer()

    class Meta:
        model = Project
        fields = FinalSelectionListSerializer.Meta.fields + ('bd', )


class ClosedProjectsListSerializer(ModelSerializer):
    function = CharField(source='function.tag_name')
    role = CharField(source='role.tag_name')
    start_date = SerializerMethodField('fetch_start_date')
    end_date = SerializerMethodField('fetch_end_date')
    recruiter = AdminInfoSerializer()
    total_no_of_days = IntegerField(source='recruitment_days')
    positions_to_be_filled = SerializerMethodField('fetch_no_of_positions')
    launch_date = SerializerMethodField('fetch_launch_date')

    @staticmethod
    def fetch_working_days(instance):
        return working_days(instance.start_date)

    @staticmethod
    def fetch_no_of_positions(instance):
        return instance.requirement_set.get_or_create()[0].no_of_positions

    @staticmethod
    def fetch_start_date(instance):
        if instance.start_date:
            return instance.start_date.strftime("%d/%m/%Y")
        return None

    @staticmethod
    def fetch_end_date(instance):
        if instance.end_date:
            return instance.end_date.strftime("%d/%m/%Y")
        return None

    @staticmethod
    def fetch_launch_date(instance):
        if instance.launch_date:
            return instance.launch_date.strftime("%d/%m/%Y")

    class Meta:
        model = Project
        fields = ('id', 'company_name', 'function', 'role', 'start_date', 'recruiter', 'total_no_of_days', 'end_date',
                  'positions_to_be_filled', 'flexibees_selected', 'client_selected', 'launch_date', )


class RecruiterAdminClosedProjectsListSerializer(ClosedProjectsListSerializer):
    bd = AdminInfoSerializer()

    class Meta:
        model = Project
        fields = ClosedProjectsListSerializer.Meta.fields + ('bd', )


class RecruiterClosedProjectsListSerializer(ClosedProjectsListSerializer):
    bd = AdminInfoSerializer()

    class Meta:
        model = Project
        fields = ('id', 'company_name', 'function', 'role', 'start_date', 'bd', 'total_no_of_days', 'end_date',
                  'positions_to_be_filled', 'flexibees_selected', 'client_selected', 'launch_date',)


class SuspendedProjectsListSerializer(ModelSerializer):
    function = CharField(source='function.tag_name')
    role = CharField(source='role.tag_name')
    start_date = SerializerMethodField('fetch_start_date')
    suspended_on = SerializerMethodField('fetch_suspended_date')
    recruiter = AdminInfoSerializer(source='previous_recruiter')

    @staticmethod
    def fetch_start_date(instance):
        if instance.start_date:
            return instance.start_date.strftime("%d/%m/%Y")

    @staticmethod
    def fetch_suspended_date(instance):
        if instance.suspended_on:
            return instance.suspended_on.strftime("%d/%m/%Y")
        return None

    class Meta:
        model = Project
        fields = ('id', 'company_name', 'function', 'role', 'start_date', 'recruiter', 'suspended_on', )


class RecruiterAdminSuspendedProjectsListSerializer(SuspendedProjectsListSerializer):
    bd = AdminInfoSerializer()

    class Meta:
        model = Project
        fields = SuspendedProjectsListSerializer.Meta.fields + ('bd', )


class RecruiterSuspendedProjectsListSerializer(SuspendedProjectsListSerializer):
    bd = AdminInfoSerializer()

    class Meta:
        model = Project
        fields = ('id', 'company_name', 'function', 'role', 'start_date', 'bd', 'suspended_on', 'notify_status', )


class ProjectUpdateSerializer(Serializer):
    client_details = DictField()
    requirement_details = DictField()
    flexi_details = DictField()
    other_details = DictField()


class SuspendedProjectSerializer(ModelSerializer):

    class Meta:
        model = Suspended
        exclude = ('modified', 'active',)
        read_only_fields = ('id',)


class ProjectBaseUpdateSerializer(ModelSerializer):

    class Meta:
        model = Project
        fields = ('role', 'role_type', 'model_type', 'description',)


class ProjectRequirementDetailsSerializer(ModelSerializer):
    company_name = CharField(source='project.role.tag_name')
    role = CharField(source='project.role.tag_name')
    must_have_skills = SkillSerializer(many=True)
    nice_to_have_skills = SkillSerializer(many=True)

    class Meta:
        model = Requirement
        fields = ('company_name', 'role', 'no_of_positions', 'min_total_experience_needed', 'nice_to_have_skills',
                  'max_total_experience_needed', 'min_relevant_experience', 'max_relevant_experience', 'must_have_skills', )


class ClientDetailsSerializer(ModelSerializer):
    company_name = CharField(source='project.company_name')
    contact_name = CharField(source='project.contact_name')

    class Meta:
        model = ClientDetail
        fields = ('company_name', 'contact_name', 'company_website', 'company_brief', 'currency')


class FlexiDetailsSerializer(ModelSerializer):
    project_start_date = DateTimeField(source='project.start_date')
    project_end_date = DateTimeField(source='project.end_date')

    class Meta:
        model = FlexiDetails
        fields = ('location_constraints', 'selected_city', 'is_travel_required', 'how_often_travelling',
                  'company_address', 'min_no_of_working_hours', 'max_no_of_working_hours', 'working_hours_duration_unit',
                  'turn_around_time', 'turn_around_duration_unit', 'client_assignment', 'assignment_file',
                  'assignment_duration', 'selected_country', 'project_start_date', 'project_end_date', )


class OtherDetailsListSerializer(ModelSerializer):

    class Meta:
        model = OtherProjectDetail
        fields = ('compensation_from_client', 'travel_expense_reimbursement', 'other_comments', )


class ClosedProjectSerializer(ModelSerializer):

    class Meta:
        model = Closed
        exclude = ('modified', 'active',)
        read_only_fields = ('id',)


class ProjectInfoSerializer(ModelSerializer):
    role = RoleSerializer(source='project.role')
    skills = SerializerMethodField('fetch_skills')
    company_name = CharField(source='project.company_name')
    function = FunctionSerializer(source='project.function')

    def fetch_skills(self, instance):
        must_have_skills = SkillSerializer(instance.must_have_skills.all(), many=True).data
        must_have_skills = [{**a, **{'must_have': True}} for a in must_have_skills]
        nice_to_have_skills = SkillSerializer(instance.nice_to_have_skills.all(), many=True).data
        nice_to_have_skills = [{**a, **{'must_have': False}} for a in nice_to_have_skills]
        return must_have_skills + nice_to_have_skills

    class Meta:
        model = Requirement
        fields = ('min_total_experience_needed', 'max_total_experience_needed', 'min_relevant_experience',
                  'max_relevant_experience', 'no_of_positions', 'skills', 'company_name', 'role', 'project',
                  'function')


class ReopenProjectSerializer(ModelSerializer):

    class Meta:
        model = Reopen
        exclude = ('modified', 'active',)
        read_only_fields = ('id', )


class AssignRecruiterSerializer(ModelSerializer):

    class Meta:
        model = Project
        fields = ('recruiter',)


class ProjectListingSerializer(ModelSerializer):
    function_name = CharField(source='function.tag_name')
    role = CharField(source='role.tag_name')
    project_details = SerializerMethodField('fetch_project_details')

    @staticmethod
    def fetch_project_details(instance):
        pricing_obj = Pricing.objects.filter(project=instance.id, active=True).order_by('-id')
        return {
                'type_of_payout': instance.flexidetails_set.get_or_create()[0].type_of_payout,
                'min_no_of_working_hours': instance.flexidetails_set.get_or_create()[0].min_no_of_working_hours,
                'max_no_of_working_hours': instance.flexidetails_set.get_or_create()[0].max_no_of_working_hours,
                'working_hours_duration_unit': instance.flexidetails_set.get_or_create()[0].working_hours_duration_unit,
                'min_total_experience_needed': instance.requirement_set.get_or_create()[0].min_total_experience_needed,
                'max_total_experience_needed': instance.requirement_set.get_or_create()[0].max_total_experience_needed,
                'project_duration': instance.flexidetails_set.get_or_create()[0].project_duration,
                'project_duration_unit': instance.flexidetails_set.get_or_create()[0].project_duration_unit,
                'min_salary': pricing_obj[0].min_salary if pricing_obj else 0,
                'max_salary': pricing_obj[0].max_salary if pricing_obj else 0,
                'currency': instance.clientdetail_set.get_or_create()[0].currency,
                'location_constraints': instance.flexidetails_set.get_or_create()[0].location_constraints,
                'selected_city': instance.flexidetails_set.get_or_create()[0].selected_city,
                'is_travel_required': instance.flexidetails_set.get_or_create()[0].is_travel_required,
                'how_often_travelling': instance.flexidetails_set.get_or_create()[0].how_often_travelling
                        }

    class Meta:
        model = Project
        fields = ('id', 'company_name', 'function_name',  'project_details', 'role', )


class ProjectDetailSerializer(ModelSerializer):
    function_name = CharField(source='function.tag_name')
    role = CharField(source='role.tag_name')
    requirement_details = SerializerMethodField('fetch_requirement_details')
    flexi_details = SerializerMethodField('fetch_flexi_details')
    project_details = SerializerMethodField('fetch_project_details')
    other_details = SerializerMethodField('fetch_other_details')

    @staticmethod
    def fetch_requirement_details(instance):
        must_have_skills = SkillSerializer(instance.requirement_set.get_or_create()[0].must_have_skills, many=True).data
        must_have_skills = [{**a, **{'must_have': True}} for a in must_have_skills]
        nice_to_have_skills = SkillSerializer(instance.requirement_set.get_or_create()[0].nice_to_have_skills, many=True).data
        nice_to_have_skills = [{**a, **{'must_have': False}} for a in nice_to_have_skills]
        skills = must_have_skills + nice_to_have_skills
        must_have_domains = DomainSerializer(instance.requirement_set.get_or_create()[0].must_have_domains, many=True).data
        must_have_domains = [{**a, **{'must_have': True}} for a in must_have_domains]
        nice_to_have_domains = DomainSerializer(instance.requirement_set.get_or_create()[0].must_have_domains,
                                              many=True).data
        nice_to_have_domains = [{**a, **{'must_have': False}} for a in nice_to_have_domains]
        domains = must_have_domains + nice_to_have_domains
        return {
            'role_type': instance.role_type,
            'model_type': instance.model_type,
            'sale_type': instance.requirement_set.get_or_create()[0].sale_type,
            'target_audience': instance.requirement_set.get_or_create()[0].target_audience,
            'language': instance.requirement_set.get_or_create()[0].language,
            'goals': instance.requirement_set.get_or_create()[0].goals,
            'content_type': instance.requirement_set.get_or_create()[0].content_type,
            'quantum_min': instance.requirement_set.get_or_create()[0].quantum_min,
            'quantum_max': instance.requirement_set.get_or_create()[0].quantum_max,
            'quantum_unit': instance.requirement_set.get_or_create()[0].quantum_unit,
            'lead_generation_requirement': instance.requirement_set.get_or_create()[0].lead_generation_requirement,
            'no_of_positions': instance.requirement_set.get_or_create()[0].no_of_positions,
            'min_total_experience_needed': instance.requirement_set.get_or_create()[0].min_total_experience_needed,
            'max_total_experience_needed': instance.requirement_set.get_or_create()[0].max_total_experience_needed,
            'min_relevant_experience': instance.requirement_set.get_or_create()[0].min_relevant_experience,
            'max_relevant_experience': instance.requirement_set.get_or_create()[0].max_relevant_experience,
            'education': instance.requirement_set.get_or_create()[0].education,
            'skills': skills,
            'domains': domains,
            'detailed_job_description': instance.requirement_set.get_or_create()[0].detailed_job_description,
            'describe_more': instance.requirement_set.get_or_create()[0].describe_more,
        }

    @staticmethod
    def fetch_flexi_details(instance):
        return {
            'location_constraints': instance.flexidetails_set.get_or_create()[0].location_constraints,
            'selected_city': instance.flexidetails_set.get_or_create()[0].selected_city,
            'is_travel_required': instance.flexidetails_set.get_or_create()[0].is_travel_required,
            'how_often_travelling': instance.flexidetails_set.get_or_create()[0].how_often_travelling,
            'company_address': instance.flexidetails_set.get_or_create()[0].company_address
        }

    @staticmethod
    def fetch_project_details(instance):
        pricing_obj = Pricing.objects.filter(project=instance.id, active=True).order_by('-id')
        return {
            'type_of_payout': instance.flexidetails_set.get_or_create()[0].type_of_payout,
            'min_no_of_working_hours': instance.flexidetails_set.get_or_create()[0].min_no_of_working_hours,
            'max_no_of_working_hours': instance.flexidetails_set.get_or_create()[0].max_no_of_working_hours,
            'working_hours_duration_unit': instance.flexidetails_set.get_or_create()[0].working_hours_duration_unit,
            'project_duration': instance.flexidetails_set.get_or_create()[0].project_duration,
            'project_duration_unit': instance.flexidetails_set.get_or_create()[0].project_duration_unit,
            'min_salary': pricing_obj[0].min_salary if pricing_obj else 0,
            'max_salary': pricing_obj[0].max_salary if pricing_obj else 0,
            'company_website': instance.clientdetail_set.get_or_create()[0].company_website,
            'company_brief': instance.clientdetail_set.get_or_create()[0].company_brief,
            'currency': instance.clientdetail_set.get_or_create()[0].currency,
        }

    @staticmethod
    def fetch_other_details(instance):
        return {
            'client_variable': instance.otherprojectdetail_set.get_or_create()[0].client_variable,
            'compensation_structure': instance.otherprojectdetail_set.get_or_create()[0].compensation_structure,
            'phone_reimbursement': instance.otherprojectdetail_set.get_or_create()[0].phone_reimbursement,
            'travel_expense_reimbursement': instance.otherprojectdetail_set.get_or_create()[0].travel_expense_reimbursement
        }

    class Meta:
        model = Project
        fields = ('id', 'company_name', 'function_name', 'description', 'requirement_details', 'flexi_details',
                  'project_details', 'role', 'other_details', 'form_type', )


class ProjectListSerializer(ModelSerializer):
    role = CharField(source='role.tag_name')

    class Meta:
        model = Project
        fields = ('id', 'company_name', 'role',)
