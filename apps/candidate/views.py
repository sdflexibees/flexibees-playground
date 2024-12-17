from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from weasyprint import HTML
from django.db.models import Q, Case, When

from apps import candidate
from apps.admin_app.serializers import SkillSerializer
from apps.availability.serializers import CandidateTimelineSerializer, SearchWebUserSerializer
from apps.availability.views import get_question_answer, get_timeline
from apps.candidate.all_candidate import check_candidate_profile
from apps.candidate.models import Candidate, Assignment, Functional, FunctionalFeedback, InterestCheckAndSelfEvaluation, \
    AssignmentFeedback, Flexifit, FlexifitFeedback, FinalSelection, ClientFeedback, WebUser, Shortlist, SelfAssessment
from apps.candidate.serializers import AllCandidateListSerializer, CandidateProfileDetailSerializer, CandidatesListSerializer, WorkExperienceListSerializer, \
    EducationListSerializer, CertificationListSerializer, LanguageListSerializer, AttachmentListSerializer, \
    NextLevelSerializer, WebUserSerializer, WebUserListingSerializer, WorkExperienceListingSerializer, \
    CandidateDetailSerializer, CandidateSelfAssessmentSerializer, CandidateAssignmentFeedbackSerializer, \
    CandidateFunctionalFeedbackSerializer, CandidateFlexifitFeedbackSerializer, CandidateClientFeedbackSerializer, \
    WebUserSendAppLinkSerializer
from apps.projects.models import Project
from apps.projects.serializers import ProjectListSerializer

from core.api_permissions import AdminAuthentication
from core.emails import email_send
from core.pagination import paginate
from core.response_format import message_response
from core.response_messages import moved_to_next, registered, object_does_not_exist, app_links_sent, \
    already_email_registered, already_phone_registered, cannot_move_to_flexifit
from core.sms import send_sms
from core.validations import check_invalid
from core.helper_functions import min_hours_filled_in_my_typical_day


class AllCandidateViewSet(ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidatesListSerializer
