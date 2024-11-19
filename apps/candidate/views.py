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
from apps.candidate.mobility_views import CandidateActiveProjectsAPI
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


class CandidateDetailAPI(ModelViewSet):

    def retrieve(self, request, candidate, project=None):
        candidate_query = check_candidate_profile(candidate)
        timeline = get_timeline(candidate)
        my_life_question_answer_list = get_question_answer(candidate_query)
        context = {
            'profile_details': CandidateProfileDetailSerializer(candidate_query).data,
            'skills': SkillSerializer(candidate_query.skills.all(), many=True).data,
            'profile_summary': candidate_query.profile_summary,
            'work_experience': WorkExperienceListSerializer(candidate_query.employmentdetail_set.filter(active=True),
                                                            many=True).data,
            'education': EducationListSerializer(candidate_query.education_set.filter(active=True), many=True).data,
            'certifications': CertificationListSerializer(candidate_query.certification_set.filter(active=True),
                                                          many=True).data,
            'languages': LanguageListSerializer(candidate_query.candidatelanguage_set.filter(active=True),
                                                many=True).data,
            'attachments': AttachmentListSerializer(candidate_query.candidateattachment_set.filter(active=True),
                                                    many=True).data,
            'hire': candidate_query.hire,
            'timeline': CandidateTimelineSerializer(timeline, many=True).data,
            'mylife': my_life_question_answer_list
        }
        if project:
            try:
                context.update({'assignment': candidate_query.assignment_set.get(project=project).submitted_assignment})
            except:
                context.update({'assignment': None})
        return Response(context)


class WebUsersRegisterAPI(APIView):

    @swagger_auto_schema(request_body=WebUserSerializer, operation_description='User registration form to be fill with basic details.')
    def post(self, request):
        candidate_email_exists = Candidate.objects.filter(email__iexact=request.data['email'], active=True)
        candidate_phone_exists = Candidate.objects.filter(phone__iexact=request.data['phone'], active=True)
        if candidate_email_exists:
            return Response(message_response(already_email_registered), 400)
        elif candidate_phone_exists:
            return Response(message_response(already_phone_registered), 400)
        web_user_email_exists = WebUser.objects.filter(email__iexact=request.data['email'], active=True)
        web_user_phone_exists = WebUser.objects.filter(phone__iexact=request.data['phone'], active=True)
        if not web_user_email_exists and not web_user_phone_exists:
            serializers = WebUserSerializer(data=request.data)
            if serializers.is_valid():
                serializers.save()
                subject = 'Thanks for your interest - Welcome to FlexiBees'
                template = 'website_user_email.html'
                recipients = [serializers.data['email']]
                context = {
                    'username': serializers.data['first_name'],
                    'play_store_link': 't.ly/Zk0P',
                    'app_store_link': 't.ly/sPGY'
                }
                email_send(subject, template, recipients, context)
                return Response(message_response(registered), 200)
            return Response(serializers.errors, 400)
        elif web_user_email_exists:
            return Response(message_response(already_email_registered), 400)
        else:
            return Response(message_response(already_phone_registered), 400)


class CandidateResumeDownloadAPI(ModelViewSet):

    def download_resume(self, request, candidate):
        candidate_query = get_object_or_404(Candidate, id=candidate, active=True)
        context = {
            'first_name': candidate_query.first_name,
            'last_name': candidate_query.last_name,
            'profile_summary': candidate_query.profile_summary,
            'skills': SkillSerializer(candidate_query.skills.all(), many=True).data,
            'work_experience': WorkExperienceListingSerializer(
                candidate_query.employmentdetail_set.filter(active=True).order_by('-start_date'), many=True).data,
            'education': EducationListSerializer(candidate_query.education_set.filter(active=True).order_by('-start_date'), many=True).data,
            'certifications': CertificationListSerializer(candidate_query.certification_set.filter(active=True),
                                                          many=True).data,
            'languages': LanguageListSerializer(candidate_query.candidatelanguage_set.filter(active=True),
                                                many=True).data,
        }
        html_string = render_to_string('flexibees_resume_pdf.html', context)
        html = HTML(string=html_string)
        pdf = html.write_pdf()
        if pdf:
            return self._extracted_from_download_resume_13(pdf, candidate_query, request)
        return Response(message_response(object_does_not_exist), status=404)

    def _extracted_from_download_resume_13(self, pdf, candidate_query, request):
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = 'Flexibees_Resume_%s.pdf' % candidate_query.first_name
        content = "inline; filename=%s" % filename
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" % (filename)
        response['Content-Disposition'] = content
        return response


class WebsiteSendLinkAPI(ModelViewSet):

    @staticmethod
    @swagger_auto_schema(request_body=WebUserSendAppLinkSerializer)
    def send_app_link(request):
        country_code = request.data.get('country_code', '91')
        phone = request.data.get('phone')
        play_store_link = 't.ly/Zk0P'
        app_store_link = 't.ly/sPGY'
        message = 'Dear candidate, Please click on the link given to download the FlexiBees Mobile App. Create your profile easily, and let us find you part time and remote roles matched with your skills and flexibility needs.. Play store link- '+ play_store_link + ' , App store link- ' + app_store_link
        send_sms(country_code, phone, message)
        return Response(message_response(app_links_sent))
    
    
class AllCandidateViewSet(ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidatesListSerializer
