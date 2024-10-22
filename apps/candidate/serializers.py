import datetime
import dateutil.parser as parser
from dateutil import relativedelta as rdelta
from django.utils import timezone

from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from rest_framework.fields import SerializerMethodField, IntegerField, ListField, CharField, BooleanField, \
    DateTimeField, FloatField
from rest_framework.serializers import ModelSerializer, Serializer

from apps.admin_app.models import Skill
from apps.admin_app.serializers import SkillSerializer, RoleSerializer, DomainSerializer, LanguageSerializer
from apps.candidate.models import Candidate, EmploymentDetail, Education, Certification, CandidateLanguage, \
    CandidateAttachment, Shortlist, InterestCheckAndSelfEvaluation, Functional, Flexifit, FunctionalFeedback, \
    FlexifitFeedback, FinalSelection, ClientFeedback, Assignment, AssignmentFeedback, SelfAssessment, WebUser
from core.helper_functions import min_hours_filled_in_my_typical_day


def get_profile_percentage(user):
    result = 0
    if user.email != '' or user.phone != '':
        result += 2.5
    if user.city != '':
        result += 10
    if user.profile_pic:
        result += 2.5
    if user.profile_summary != '':
        result += 2.5
    if user.skills.all().count() != 0:
        result += 5
    if EmploymentDetail.objects.filter(active=True, candidate=user).count() != 0:
        result += 5
    if Education.objects.filter(active=True, candidate=user).count() != 0:
        result += 5
    if Certification.objects.filter(active=True, candidate=user).count() != 0:
        result += 5
    if CandidateLanguage.objects.filter(active=True, candidate=user).count() != 0:
        result += 5
    if CandidateAttachment.objects.filter(active=True, candidate=user).count() != 0:
        result += 2.5
    if user.portfolio_link:
        result += 5
    if user.questionnaire_completed:
        result += 10
    if min_hours_filled_in_my_typical_day(user.id):
        result += 40
    return result


def get_must_have(context, instance):
    must_have_skills = context.get('must_have_skills', [])
    willing_to_travel = context.get('willing_to_travel', False)
    city = context.get('city', '')
    try:
        candidate_city = instance.city
    except:
        candidate_city = instance.candidate.city
    if not willing_to_travel or candidate_city == city:
        city_match = True
    elif willing_to_travel and city=='':
        city_match = True
    else:
        city_match = False
    min_no_of_working_hours = context.get('min_no_of_working_hours', 0)
    try:
        return not set(must_have_skills).isdisjoint(instance.skills.all().values_list('id', flat=True)) and \
               min_no_of_working_hours <= instance.total_available_hours and city_match
    except:
        return not set(must_have_skills).isdisjoint(instance.candidate.skills.all().values_list('id', flat=True)) and \
               min_no_of_working_hours <= instance.candidate.total_available_hours and city_match


def get_availability(context, instance):
    min_no_of_working_hours = context.get('min_no_of_working_hours')
    availability = 'red'
    try:
        candidate_total_available_hours = instance.candidate.total_available_hours
    except:
        candidate_total_available_hours = instance.total_available_hours
    if min_no_of_working_hours <= candidate_total_available_hours:
        availability = 'green'
    return availability


class AllCandidateListSerializer(ModelSerializer):
    skills = SkillSerializer(many=True)
    roles = RoleSerializer(many=True)
    must_have_skills = SerializerMethodField('fetch_must_have')
    relevant_experience = SerializerMethodField('fetch_relevant_exp')
    availability = SerializerMethodField('fetch_availability')
    candidate_city = SerializerMethodField('fetch_candidate_city')

    def fetch_relevant_exp(self, instance):
        role = self.context.get('project_role')
        return instance.relevantexp['r' + role] if instance.relevantexp.get('r' + role) else 0

    def fetch_must_have(self, instance):
        context = self.context
        return get_must_have(context, instance)



    def fetch_candidate_city(self,instance):
        try:
            candidate_city = instance.city
        except:
            candidate_city = instance.candidate.city
        return candidate_city

    def fetch_availability(self, instance):
        context = self.context
        return get_availability(context, instance)

    class Meta:
        model = Candidate
        fields = ('id', 'first_name', 'skills', 'total_year_of_experience', 'relevant_experience', 'must_have_skills',
                  'roles', 'hire', 'timeline_completed', 'total_available_hours', 'availability', 'active_projects',
                  'flexibees_selected','candidate_city')


class CandidateProfileDetailSerializer(ModelSerializer):
    class Meta:
        model = Candidate
        fields = ('id', 'first_name', 'last_name', 'date_of_birth', 'email', 'country_code', 'phone', 'city',
                  'profile_pic', 'will_to_travel_to_local_office', 'hear_about_flexibees', 'brief_description',
                  'hear_about_detailed',)


class WorkExperienceListSerializer(ModelSerializer):
    role = RoleSerializer()
    domains = DomainSerializer(many=True)

    class Meta:
        model = EmploymentDetail
        exclude = ('active', 'created', 'modified', 'candidate')


class WorkExperienceListingSerializer(ModelSerializer):
    role = RoleSerializer()
    domains = DomainSerializer(many=True)
    start_date = SerializerMethodField('fetch_start_date')
    end_date = SerializerMethodField('fetch_end_date')

    @staticmethod
    def fetch_start_date(instance):
        start_date = datetime.datetime.strptime(str(instance.start_date), '%Y-%m-%d')
        start_date = start_date.strftime('%B, %Y')
        return start_date

    @staticmethod
    def fetch_end_date(instance):
        if instance.end_date:
            end_date = datetime.datetime.strptime(str(instance.end_date), '%Y-%m-%d')
            end_date = end_date.strftime('%B, %Y')
            return end_date

    class Meta:
        model = EmploymentDetail
        fields = ('id','role', 'employment_type','company', 'currently_working', 'start_date', 'end_date', 'domains',
                  'description')


class EducationListSerializer(ModelSerializer):
    class Meta:
        model = Education
        exclude = ('active', 'created', 'modified', 'candidate')


class CertificationListSerializer(ModelSerializer):
    class Meta:
        model = Certification
        exclude = ('active', 'created', 'modified', 'candidate')


class LanguageListSerializer(ModelSerializer):
    language = LanguageSerializer()

    class Meta:
        model = CandidateLanguage
        exclude = ('active', 'created', 'modified', 'candidate')


class AttachmentListSerializer(ModelSerializer):
    class Meta:
        model = CandidateAttachment
        exclude = ('active', 'modified', 'candidate')


class ShortlistSerializer(ModelSerializer):
    candidates = ListField()

    class Meta:
        model = Shortlist
        fields = ('candidates', 'project',)


class AllCandidateListingSerializer(ModelSerializer):
    skills = SkillSerializer(many=True)
    roles = RoleSerializer(many=True)


    class Meta:
        model = Candidate
        fields = ('id', 'first_name', 'last_name', 'city', 'roles', 'skills', 'total_year_of_experience',
                  'years_of_break', 'flexibees_selected', 'active_projects', 'hire', 'active_projects',
                  'timeline_completed', 'total_available_hours',)


class AllCandidateCitySerializer(ModelSerializer):
    class Meta:
        model = Candidate
        fields = ('city',)


class CandidateShortListSerializer(AllCandidateListSerializer):
    first_name = CharField(source='candidate.first_name')
    skills = SerializerMethodField('fetch_skills')
    roles = SerializerMethodField('fetch_roles')
    total_year_of_experience = FloatField(source='candidate.total_year_of_experience')
    must_have_skills = SerializerMethodField('fetch_must_have')
    candidate_id = IntegerField(source='candidate.id')
    relevant_experience = SerializerMethodField('fetch_relevant_exp')
    total_available_hours = FloatField(source='candidate.total_available_hours')
    timeline_completed = BooleanField(source='candidate.timeline_completed')
    availability = SerializerMethodField('fetch_candidate_availability')
    hire = BooleanField(source='candidate.hire')
    active = BooleanField(source='candidate.active')
    active_projects = IntegerField(source='candidate.active_projects')
    flexibees_selected = IntegerField(source='candidate.flexibees_selected')

    def fetch_relevant_exp(self, instance):
        role = self.context.get('project_role')
        return instance.candidate.relevantexp['r' + role] if instance.candidate.relevantexp.get('r' + role) else 0

    @staticmethod
    def fetch_skills(instance):
        return SkillSerializer(instance.candidate.skills.all(), many=True).data

    @staticmethod
    def fetch_roles(instance):
        return RoleSerializer(instance.candidate.roles.all(), many=True).data

    def fetch_must_have(self, instance):
        context = self.context
        return get_must_have(context, instance)

    def fetch_candidate_availability(self, instance):
        context = self.context
        return get_availability(context, instance)

    class Meta:
        model = Shortlist
        fields = ('id', 'first_name', 'total_year_of_experience', 'relevant_experience', 'must_have_skills', 'skills',
                  'roles', 'status', 'hire', 'active', 'candidate_id', 'total_available_hours', 'timeline_completed',
                  'availability', 'active_projects', 'flexibees_selected',)


class InterestCheckAndSelfEvaluationSerializer(AllCandidateListSerializer):
    first_name = CharField(source='candidate.first_name')
    skills = SerializerMethodField('fetch_skills')
    roles = SerializerMethodField('fetch_roles')
    must_have_skills = SerializerMethodField('fetch_must_have')
    candidate_id = IntegerField(source='candidate.id')
    next_level = SerializerMethodField('fetch_next_level')
    total_available_hours = FloatField(source='candidate.total_available_hours')
    timeline_completed = BooleanField(source='candidate.timeline_completed')
    availability = SerializerMethodField('fetch_candidate_availability')
    hire = BooleanField(source='candidate.hire')
    active = BooleanField(source='candidate.active')
    active_projects = IntegerField(source='candidate.active_projects')
    flexibees_selected = IntegerField(source='candidate.flexibees_selected')

    def fetch_next_level(self, instance):
        similar_projects = self.context.get('similar_projects', [])
        similar_assignment = Assignment.objects.filter(project__in=similar_projects, status=4,
                                                       candidate=instance.candidate).last()
        return {
            'eligible': bool(similar_assignment),
            'assignment': similar_assignment.submitted_assignment if similar_assignment else None,
            'assignment_id': similar_assignment.id if similar_assignment else None,
        }

    @staticmethod
    def fetch_skills(instance):
        return SkillSerializer(instance.candidate.skills.all(), many=True).data

    @staticmethod
    def fetch_roles(instance):
        return RoleSerializer(instance.candidate.roles.all(), many=True).data

    def fetch_must_have(self, instance):
        context = self.context
        return get_must_have(context, instance)

    def fetch_candidate_availability(self, instance):
        context = self.context
        return get_availability(context, instance)

    class Meta:
        model = InterestCheckAndSelfEvaluation
        fields = ('id', 'first_name', 'must_have_skills', 'skills', 'roles', 'status', 'hire', 'active', 'flexibees_selected',
                  'candidate_id', 'next_level', 'total_available_hours', 'timeline_completed', 'availability', 'active_projects',)


class ShortlistNotificationSerializer(Serializer):
    shortlisted_candidates = ListField(default=[])
    title = CharField(required=True)
    description = CharField(required=True)

    class Meta:
        fields = ('shortlisted_candidates', 'title', 'description')


class CandidateFunctionalSerializer(AllCandidateListSerializer):
    first_name = CharField(source='candidate.first_name')
    skills = SerializerMethodField('fetch_skills')
    roles = SerializerMethodField('fetch_roles')
    must_have_skills = SerializerMethodField('fetch_must_have')
    candidate_id = IntegerField(source='candidate.id')
    feedback = SerializerMethodField('fetch_feedback')
    next_level = SerializerMethodField('fetch_next_level')
    total_available_hours = FloatField(source='candidate.total_available_hours')
    timeline_completed = BooleanField(source='candidate.timeline_completed')
    availability = SerializerMethodField('fetch_candidate_availability')
    hire = BooleanField(source='candidate.hire')
    active = BooleanField(source='candidate.active')
    active_projects = IntegerField(source='candidate.active_projects')
    flexibees_selected = IntegerField(source='candidate.flexibees_selected')
    is_my_life_updated = SerializerMethodField('check_my_life')
    is_my_typical_day_updated = SerializerMethodField('check_typical_day')

    def fetch_next_level(self, instance):
        similar_projects = self.context.get('similar_projects', [])
        similar_functional = Flexifit.objects.filter(project__in=similar_projects, status=2,
                                                     candidate=instance.candidate).last()
        return {
            'eligible': bool(similar_functional),
            'flexifit_id': similar_functional.id if similar_functional else None,
        }

    @staticmethod
    def fetch_skills(instance):
        return SkillSerializer(instance.candidate.skills.all(), many=True).data

    @staticmethod
    def fetch_roles(instance):
        return RoleSerializer(instance.candidate.roles.all(), many=True).data

    def fetch_must_have(self, instance):
        context = self.context
        return get_must_have(context, instance)

    @staticmethod
    def fetch_feedback(instance):
        functional_obj = FunctionalFeedback.objects.filter(functional=instance.id, active=True)
        return bool(functional_obj)

    def fetch_candidate_availability(self, instance):
        context = self.context
        return get_availability(context, instance)
    
    @staticmethod
    def check_typical_day(instance):
        return min_hours_filled_in_my_typical_day(instance.candidate.id)
    
    @staticmethod
    def check_my_life(instance):
        return bool(len(list(instance.candidate.lifestyle_responses)))

    class Meta:
        model = Functional
        fields = ('id', 'first_name', 'must_have_skills', 'skills', 'roles', 'status', 'hire', 'active',
                  'candidate_id', 'feedback', 'next_level', 'total_available_hours', 'timeline_completed',
                  'availability', 'active_projects', 'flexibees_selected','is_my_life_updated', 
                  'is_my_typical_day_updated', 'no_of_notifications_on_my_typical_day', 'last_notified')


class CandidateFlexifitSerializer(AllCandidateListSerializer):
    first_name = CharField(source='candidate.first_name')
    skills = SerializerMethodField('fetch_skills')
    roles = SerializerMethodField('fetch_roles')
    must_have_skills = SerializerMethodField('fetch_must_have')
    candidate_id = IntegerField(source='candidate.id')
    feedback = SerializerMethodField('fetch_feedback')
    next_level = SerializerMethodField('fetch_next_level')
    total_available_hours = FloatField(source='candidate.total_available_hours')
    timeline_completed = BooleanField(source='candidate.timeline_completed')
    availability = SerializerMethodField('fetch_candidate_availability')
    hire = BooleanField(source='candidate.hire')
    active = BooleanField(source='candidate.active')
    active_projects = IntegerField(source='candidate.active_projects')
    flexibees_selected = IntegerField(source='candidate.flexibees_selected')

    def fetch_next_level(self, instance):
        similar_projects = self.context.get('similar_projects', [])
        similar_functional = FinalSelection.objects.filter(project__in=similar_projects, status=3,
                                                           candidate=instance.candidate).last()
        return {
            'eligible': bool(similar_functional),
            'final_selection_id': similar_functional.id
            if similar_functional
            else None,
        }

    @staticmethod
    def fetch_skills(instance):
        return SkillSerializer(instance.candidate.skills.all(), many=True).data

    @staticmethod
    def fetch_roles(instance):
        return RoleSerializer(instance.candidate.roles.all(), many=True).data

    def fetch_must_have(self, instance):
        context = self.context
        return get_must_have(context, instance)

    @staticmethod
    def fetch_feedback(instance):
        flexifit_obj = FlexifitFeedback.objects.filter(flexifit=instance.id, active=True)
        return bool(flexifit_obj)

    def fetch_candidate_availability(self, instance):
        context = self.context
        return get_availability(context, instance)

    class Meta:
        model = Flexifit
        fields = ('id', 'first_name', 'must_have_skills', 'skills', 'roles', 'status', 'hire', 'active',
                  'candidate_id', 'feedback', 'next_level', 'total_available_hours', 'timeline_completed',
                  'availability', 'active_projects', 'flexibees_selected',)


class FunctionalFeedbackSerializer(ModelSerializer):
    class Meta:
        model = FunctionalFeedback
        exclude = ('active', 'created', 'modified',)


class FunctionalFeedbackViewSerializer(ModelSerializer):
    skills_feedback = SerializerMethodField('fetch_skills_feedback')
    candidate_name = CharField(source='functional.candidate.first_name')

    @staticmethod
    def fetch_skills_feedback(instance):
        skills_feedback = not any(instance.skills_feedback)
        if not skills_feedback:
            skills_feedback_list = []
            for data in instance.skills_feedback:
                data['skill'] = Skill.objects.filter(active=True, tag_name=data['skill']).values_list('tag_name')[0][0]
                skills_feedback_list.append(data)
            return skills_feedback_list

    class Meta:
        model = FunctionalFeedback
        fields = (
            'id', 'overall_score', 'skills_feedback', 'recommendation', 'comments', 'interview_summary',
            'candidate_name',)


class FlexifitFeedbackSerializer(ModelSerializer):
    class Meta:
        model = FlexifitFeedback
        exclude = ('active', 'created', 'modified',)


class FlexifitFeedbackViewSerializer(ModelSerializer):
    candidate_name = CharField(source='flexifit.candidate.first_name')

    class Meta:
        model = FlexifitFeedback
        fields = ('id', 'recommendation', 'comments', 'candidate_name', 'interview_summary')


class FinalSelectionListSerializer(ModelSerializer):
    first_name = CharField(source='candidate.first_name')
    skills = SkillSerializer(source='candidate.skills', many=True)
    roles = RoleSerializer(source='candidate.roles', many=True)
    hire = BooleanField(source='candidate.hire')
    candidate_id = IntegerField(source='candidate.id')
    flexifit = IntegerField(source='flexifit_feedback.flexifit.id')
    total_available_hours = FloatField(source='candidate.total_available_hours')
    timeline_completed = BooleanField(source='candidate.timeline_completed')
    availability = SerializerMethodField('fetch_candidate_availability')
    active_projects = IntegerField(source='candidate.active_projects')
    flexibees_selected = IntegerField(source='candidate.flexibees_selected')

    def fetch_candidate_availability(self, instance):
        context = self.context
        return get_availability(context, instance)

    class Meta:
        model = FinalSelection
        fields = ('id', 'first_name', 'skills', 'roles', 'status', 'hire', 'candidate_id', 'flexifit_feedback',
                  'flexifit', 'total_available_hours', 'timeline_completed', 'availability', 'active_projects',
                  'flexibees_selected', 'recruiter_comments', 'final_notification_sent',)


class ClientFeedbackSerializer(ModelSerializer):
    class Meta:
        model = ClientFeedback
        exclude = ('active', 'created', 'modified',)


class ClientFeedbackViewSerializer(ModelSerializer):
    candidate_name = CharField(source='final_selection.candidate.first_name')

    class Meta:
        model = ClientFeedback
        fields = ('id', 'recommendation', 'comments', 'candidate_name',)


class CandidateAssignmentSerializer(AllCandidateListSerializer):
    first_name = CharField(source='candidate.first_name')
    skills = SerializerMethodField('fetch_skills')
    roles = SerializerMethodField('fetch_roles')
    must_have_skills = SerializerMethodField('fetch_must_have')
    candidate_id = IntegerField(source='candidate.id')
    feedback = SerializerMethodField('fetch_feedback')
    due_date_over = SerializerMethodField('fetch_due_date')
    next_level = SerializerMethodField('fetch_next_level')
    total_available_hours = FloatField(source='candidate.total_available_hours')
    timeline_completed = BooleanField(source='candidate.timeline_completed')
    availability = SerializerMethodField('fetch_candidate_availability')
    hire = BooleanField(source='candidate.hire')
    active = BooleanField(source='candidate.active')
    active_projects = IntegerField(source='candidate.active_projects')
    flexibees_selected = IntegerField(source='candidate.flexibees_selected')

    def fetch_next_level(self, instance):
        similar_projects = self.context.get('similar_projects', [])
        similar_functional = Functional.objects.filter(project__in=similar_projects, status=2,
                                                       candidate=instance.candidate).last()
        return {
            'eligible': bool(similar_functional),
            'functional_id': similar_functional.id if similar_functional else None,
        }

    @staticmethod
    def fetch_due_date(instance):
        if instance.due_date:
            return instance.due_date < now()
        return False

    @staticmethod
    def fetch_skills(instance):
        return SkillSerializer(instance.candidate.skills.all(), many=True).data

    @staticmethod
    def fetch_roles(instance):
        return RoleSerializer(instance.candidate.roles.all(), many=True).data

    def fetch_must_have(self, instance):
        context = self.context
        return get_must_have(context, instance)

    @staticmethod
    def fetch_feedback(instance):
        assignment_obj = AssignmentFeedback.objects.filter(assignment=instance.id, active=True)
        return bool(assignment_obj)

    def fetch_candidate_availability(self, instance):
        context = self.context
        return get_availability(context, instance)

    class Meta:
        model = Assignment
        fields = ('id', 'first_name', 'must_have_skills', 'skills', 'roles', 'status', 'hire', 'active',
                  'candidate_id', 'feedback', 'submitted_assignment', 'due_date_over', 'next_level',
                  'total_available_hours', 'timeline_completed', 'availability', 'active_projects', 'flexibees_selected',)


class AssignmentFeedbackSerializer(ModelSerializer):
    class Meta:
        model = AssignmentFeedback
        exclude = ('active', 'created', 'modified',)


class AssignmentFeedbackViewSerializer(ModelSerializer):
    candidate_name = CharField(source='assignment.candidate.first_name')

    # skills_feedback = SerializerMethodField('fetch_skills_feedback')
    #
    # @staticmethod
    # def fetch_skills_feedback(instance):
    #     if instance.skills_feedback:
    #         skills_feedback_list = list()
    #         for data in instance.skills_feedback:
    #             data['skill'] = Skill.objects.filter(active=True, id=data['skill']).values_list('tag_name')[0][0]
    #             skills_feedback_list.append(data)
    #         return skills_feedback_list

    class Meta:
        model = AssignmentFeedback
        fields = ('id', 'recommendation', 'comments', 'candidate_name',)


class FunctionalSerializer(ModelSerializer):
    class Meta:
        model = Functional
        exclude = ('active', 'modified',)


class FlexifitSerializer(ModelSerializer):
    class Meta:
        model = Flexifit
        exclude = ('active', 'modified',)


class NextLevelSerializer(Serializer):
    next_stage = CharField(default='assignment')
    current_stage_id = IntegerField(required=True)
    next_stage_id = IntegerField(required=True)

    class Meta:
        fields = ('next_stage', 'current_stage_id', 'next_stage_id',)


class CandidateSerializer(ModelSerializer):
    class Meta:
        model = Candidate
        exclude = ('active', 'modified',)


class CandidateDetailsSerializer(ModelSerializer):
    profile_percentage = SerializerMethodField('fetch_profile_percentage')
    modified = DateTimeField(source='profile_last_updated')

    @staticmethod
    def fetch_profile_percentage(instance):
        return get_profile_percentage(instance)

    class Meta:
        model = Candidate
        fields = ('id', 'first_name', 'last_name', 'date_of_birth', 'email', 'country_code', 'phone', 'city', 'country',
                  'profile_pic', 'will_to_travel_to_local_office', 'hear_about_flexibees', 'active_projects',
                  'profile_summary', 'skills', 'roles', 'total_year_of_experience', 'relevant_experience',
                  'relevantexp', 'years_of_break', 'hire', 'portfolio_link', 'address', 'legacy_skills',
                  'phone_verified', 'email_verified', 'created', 'profile_percentage', 'modified', 'active_projects',
                  'hear_about_detailed', 'last_login', )


class CandidateProfileSerializer(ModelSerializer):
    class Meta:
        model = Candidate
        fields = ('id', 'first_name', 'last_name', 'date_of_birth', 'email', 'country_code', 'phone', 'city',
                  'profile_pic', 'hear_about_flexibees', 'profile_summary', 'skills', 'country',
                  'hear_about_detailed', 'profile_last_updated',)


class CandidateBasicProfileViewSerializer(ModelSerializer):
    skills = SkillSerializer(many=True)

    class Meta:
        model = Candidate
        fields = ('id', 'first_name', 'last_name', 'date_of_birth', 'email', 'country_code', 'phone', 'city',
                  'profile_pic', 'hear_about_flexibees', 'profile_summary', 'skills',
                  'phone_verified', 'email_verified', 'hear_about_detailed',)


class CandidateWorkExperienceSerializer(ModelSerializer):
    class Meta:
        model = EmploymentDetail
        fields = ('id', 'candidate', 'role', 'employment_type', 'company', 'currently_working', 'start_date',
                  'end_date', 'domains', 'description', 'created',)


class CandidateWorkExperienceViewSerializer(CandidateWorkExperienceSerializer):
    domains = DomainSerializer(many=True)
    role = RoleSerializer()
    duration = SerializerMethodField('fetch_duration')
    profile_percentage = SerializerMethodField('fetch_profile_percentage')
    modified = DateTimeField(source='candidate.modified')

    @staticmethod
    def fetch_duration(instance):
        start_date = parser.parse(str(instance.start_date))
        if not instance.end_date:
            end_date = parser.parse(str(timezone.now().date()))
        else:
            end_date = parser.parse(str(instance.end_date))
        rd = rdelta.relativedelta(end_date, start_date)
        return {"years": rd.years, "months": rd.months, "days": rd.days}

    @staticmethod
    def fetch_profile_percentage(instance):
        return get_profile_percentage(instance.candidate)

    class Meta:
        model = EmploymentDetail
        fields = CandidateWorkExperienceSerializer.Meta.fields + ('duration', 'profile_percentage', 'modified',)


class CandidateEducationSerializer(ModelSerializer):
    class Meta:
        model = Education
        fields = (
            'id', 'candidate', 'school_college', 'education', 'course', 'field_of_study', 'start_date', 'end_date',
            'grade', 'description', 'created',)


class CandidateEducationViewSerializer(CandidateEducationSerializer):
    profile_percentage = SerializerMethodField('fetch_profile_percentage')
    modified = DateTimeField(source='candidate.modified')
    duration = SerializerMethodField('fetch_duration')

    @staticmethod
    def fetch_profile_percentage(instance):
        return get_profile_percentage(instance.candidate)

    @staticmethod
    def fetch_duration(instance):
        return instance.end_date - instance.start_date

    class Meta:
        model = Education
        fields = CandidateEducationSerializer.Meta.fields + ('profile_percentage', 'modified', 'duration',)


class CandidateCertificationSerializer(ModelSerializer):
    class Meta:
        model = Certification
        fields = ('id', 'candidate', 'title', 'issued_by', 'issue_date', 'created',)


class CandidateCertificationViewSerializer(CandidateCertificationSerializer):
    profile_percentage = SerializerMethodField('fetch_profile_percentage')
    modified = DateTimeField(source='candidate.modified')

    @staticmethod
    def fetch_profile_percentage(instance):
        return get_profile_percentage(instance.candidate)

    class Meta:
        model = Certification
        fields = CandidateCertificationSerializer.Meta.fields + ('profile_percentage', 'modified',)


class CandidateLanguageSerializer(ModelSerializer):
    class Meta:
        model = CandidateLanguage
        fields = ('id', 'candidate', 'language', 'proficiency', 'read', 'write', 'speak', 'created',)


class CandidateLanguageViewSerializer(CandidateLanguageSerializer):
    profile_percentage = SerializerMethodField('fetch_profile_percentage')
    modified = DateTimeField(source='candidate.modified')
    language = LanguageSerializer()

    @staticmethod
    def fetch_profile_percentage(instance):
        return get_profile_percentage(instance.candidate)

    class Meta:
        model = CandidateLanguage
        fields = CandidateLanguageSerializer.Meta.fields + ('profile_percentage', 'modified',)


class CandidateAttachmentSerializer(ModelSerializer):
    class Meta:
        model = CandidateAttachment
        fields = ('id', 'candidate', 'attachment', 'title', 'created',)


class CandidateAttachmentViewSerializer(CandidateAttachmentSerializer):
    profile_percentage = SerializerMethodField('fetch_profile_percentage')
    modified = DateTimeField(source='candidate.modified')

    @staticmethod
    def fetch_profile_percentage(instance):
        return get_profile_percentage(instance.candidate)

    class Meta:
        model = CandidateAttachment
        fields = CandidateAttachmentSerializer.Meta.fields + ('profile_percentage', 'modified',)


class CandidateOtherDetailsSerializer(ModelSerializer):
    class Meta:
        model = Candidate
        fields = ('portfolio_link', 'address', 'profile_last_updated',)


class CandidateOtherDetailsViewSerializer(CandidateOtherDetailsSerializer):
    profile_percentage = SerializerMethodField('fetch_profile_percentage')

    @staticmethod
    def fetch_profile_percentage(instance):
        return get_profile_percentage(instance)

    class Meta:
        model = Candidate
        fields = CandidateOtherDetailsSerializer.Meta.fields + ('profile_percentage', 'modified',)


class CandidateProfileViewSerializer(ModelSerializer):
    skills = SkillSerializer(many=True)
    work_experience = SerializerMethodField('fetch_work_experience')
    education = SerializerMethodField('fetch_education')
    certifications = SerializerMethodField('fetch_certifications')
    languages = SerializerMethodField('fetch_languages')
    attachment = SerializerMethodField('fetch_attachment')
    other_details = SerializerMethodField('fetch_other_details')
    profile_percentage = SerializerMethodField('fetch_profile_percentage')

    @staticmethod
    def fetch_profile_percentage(instance):
        return get_profile_percentage(instance)

    @staticmethod
    def fetch_work_experience(instance):
        employment_detail_query = EmploymentDetail.objects.filter(active=True, candidate=instance.id).order_by(
            '-start_date')
        if employment_detail_query:
            return CandidateWorkExperienceViewSerializer(employment_detail_query, many=True).data

    @staticmethod
    def fetch_education(instance):
        education_query = Education.objects.filter(active=True, candidate=instance.id).order_by('-start_date')
        if education_query:
            return CandidateEducationViewSerializer(education_query, many=True).data

    @staticmethod
    def fetch_certifications(instance):
        certification_query = Certification.objects.filter(active=True, candidate=instance.id)
        if certification_query:
            return CandidateCertificationSerializer(certification_query, many=True).data

    @staticmethod
    def fetch_languages(instance):
        language_query = CandidateLanguage.objects.filter(active=True, candidate=instance.id)
        if language_query:
            return CandidateLanguageViewSerializer(language_query, many=True).data

    @staticmethod
    def fetch_attachment(instance):
        attachment_query = CandidateAttachment.objects.filter(active=True, candidate=instance.id)
        if attachment_query:
            return CandidateAttachmentSerializer(attachment_query[0]).data

    @staticmethod
    def fetch_other_details(instance):
        candidate_query = get_object_or_404(Candidate, active=True, id=instance.id)
        if not candidate_query.portfolio_link and candidate_query.address == '':
            return None
        return {'portfolio_link': candidate_query.portfolio_link, 'address': candidate_query.address}

    class Meta:
        model = Candidate
        fields = ('id', 'first_name', 'last_name', 'city', 'profile_pic', 'profile_summary', 'skills',
                  'work_experience', 'education', 'certifications', 'languages', 'attachment', 'other_details',
                  'profile_percentage', 'country', 'phone_verified', 'email_verified', 'modified',)


class SelfAssessmentSerializer(ModelSerializer):
    class Meta:
        model = SelfAssessment
        fields = ('id', 'candidate', 'project', 'skills', 'comments', 'created',)


class AssignmentSerializer(ModelSerializer):
    class Meta:
        model = Assignment
        fields = ('submitted_assignment', 'submitted_date', 'status',)


class FunctionalInterviewScheduledSerializer(ModelSerializer):
    role = CharField(source='project.role.tag_name')

    class Meta:
        model = Functional
        fields = ('scheduled_date', 'start_time', 'end_time', 'role',)


class FlexifitInterviewScheduledSerializer(ModelSerializer):
    role = CharField(source='project.role.tag_name')

    class Meta:
        model = Flexifit
        fields = ('scheduled_date', 'start_time', 'end_time', 'role',)


class WebUserSerializer(ModelSerializer):

    class Meta:
        model = WebUser
        fields = ('id', 'first_name', 'last_name', 'email', 'country_code', 'phone',)


class WebUserListingSerializer(ModelSerializer):
    no_of_days_lapsed = SerializerMethodField('fetch_no_of_days_lapsed')

    @staticmethod
    def fetch_no_of_days_lapsed(instance):
        no_of_days_lapsed = timezone.now().date() - instance.created.date()
        return no_of_days_lapsed.days

    class Meta:
        model = WebUser
        fields = ('id', 'first_name', 'last_name', 'email', 'country_code', 'phone', 'no_of_days_lapsed',)


class CandidateDetailSerializer(ModelSerializer):

    class Meta:
        model = Candidate
        fields = ('id', 'first_name', 'last_name', 'profile_pic',)


class CandidateSelfAssessmentSerializer(ModelSerializer):
    skills = SerializerMethodField('fetch_skills')

    @staticmethod
    def fetch_skills(instance):
        return [
            {
                'skill': SkillSerializer(
                    Skill.objects.get(id=skill['skill'])
                ).data,
                'level': skill['level'],
            }
            for skill in instance.skills
        ]

    class Meta:
        model = SelfAssessment
        fields = ('id', 'skills', 'comments', 'modified', )


class CandidateAssignmentFeedbackSerializer(ModelSerializer):

    class Meta:
        model = AssignmentFeedback
        fields = ('id', 'recommendation', 'comments', 'modified', )


class CandidateFunctionalFeedbackSerializer(ModelSerializer):
    skills_feedback = SerializerMethodField('fetch_skills_feedback')

    @staticmethod
    def fetch_skills_feedback(instance):
        skills_feedback = not any(instance.skills_feedback)
        if not skills_feedback:
            skills_feedback_list = []
            for data in instance.skills_feedback:
                data['skill'] = Skill.objects.filter(active=True, tag_name=data['skill']).values_list('tag_name')[0][0]
                skills_feedback_list.append(data)
            return skills_feedback_list

    class Meta:
        model = FunctionalFeedback
        fields = (
            'id', 'overall_score', 'skills_feedback', 'recommendation', 'comments', 'interview_summary', 'modified', )


class CandidateFlexifitFeedbackSerializer(ModelSerializer):

    class Meta:
        model = FlexifitFeedback
        fields = ('id', 'recommendation', 'comments', 'interview_summary', 'modified', )


class CandidateClientFeedbackSerializer(ModelSerializer):
    overall_feedback = CharField(source='final_selection.recruiter_comments')

    class Meta:
        model = ClientFeedback
        fields = ('id', 'recommendation', 'comments', 'modified', 'overall_feedback', )


class WebUserSendAppLinkSerializer(ModelSerializer):

    class Meta:
        model = WebUser
        fields = ('country_code', 'phone',)
