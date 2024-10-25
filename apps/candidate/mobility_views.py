import string
from random import choice
from dateutil import relativedelta as rdelta
from django.db.models import Q, Case, When
from django.utils import timezone

from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps import candidate
from apps.admin_app.models import AdminUser, Skill, Role, Domain, Language, AppVersion, City, Country
from apps.admin_app.serializers import SkillSerializer, RoleSerializer, DomainSerializer, LanguageSerializer, \
    AppVersionSerializer
from apps.availability.views import get_question_key, reset_typical_day_detail
from apps.candidate.models import Candidate, EmploymentDetail, Education, Certification, CandidateLanguage, \
    CandidateAttachment, Assignment, Functional, Flexifit, FinalSelection, Shortlist, InterestCheckAndSelfEvaluation, \
    ClientFeedback, WebUser

from rest_framework import exceptions
from core.model_choices import DEVICE_TYPES
from flexibees_candidate.settings import APPTEST_USERID

from apps.candidate.serializers import CandidateSerializer, CandidateDetailsSerializer, CandidateProfileSerializer, \
    CandidateWorkExperienceSerializer, CandidateEducationSerializer, CandidateCertificationSerializer, \
    CandidateLanguageSerializer, CandidateAttachmentSerializer, CandidateOtherDetailsSerializer, \
    CandidateProfileViewSerializer, CandidateBasicProfileViewSerializer, CandidateWorkExperienceViewSerializer, \
    CandidateEducationViewSerializer, CandidateCertificationViewSerializer, CandidateLanguageViewSerializer, \
    CandidateAttachmentViewSerializer, CandidateOtherDetailsViewSerializer, SelfAssessmentSerializer, \
    AssignmentSerializer, FunctionalInterviewScheduledSerializer, FlexifitInterviewScheduledSerializer, \
    get_profile_percentage
from apps.candidate.swagger_serializers import LoginSerializer, SignupSerializer, VerifyOTPSerializer
from apps.notifications.views import notify_admin
from apps.projects.models import Project
from apps.projects.serializers import ProjectListingSerializer, ProjectDetailSerializer
from core.api_permissions import AppUserAuthentication, AppVersionPermission
from core.authentication import candidate_authenticate, candidate_verify_otp
from core.emails import email_send
from core.encryption import jwt_payload_handler, jwt_encode_handler
from core.fcm import send_candidate_notification
from core.notification_contents import candidate_welcome, candidate_typical_day_notification, referral_text
from core.response_format import message_response
from core.response_messages import user_email_exists, user_phone_exists, verification_failed, deleted, \
    user_does_not_exist, email_verified, phone_verified, cannot_update_profile, user_exist, successfully_sent, \
    cannot_delete_profile, self_assessment_completed, updated, currently_working, check_dates, assignment_uploaded, \
    cannot_update_status, language_exists, lifestyle_updated, select_one_lifestyle, invalid_input, not_found, \
    cannot_access_project_details, cannot_access_project_details_for_not_hire, something_went_wrong, already_email_verified
from django.core.exceptions import ObjectDoesNotExist

from core.sms import send_sms
from core.validations import check_invalid
from flexibees_candidate.settings import SUPER_ADMIN_ROLE, SUPER_ADMIN_EMAIL, ITEM_TYPE_CANDIDATE, SENT_TO_TYPE_SUPER_ADMIN, SENT_TO_TYPE_RECRUITER, SENT_TO_TYPE_RECRUITER_ADMIN
from scripts.on_demand_task import get_mylife_status
from core.helper_functions import min_hours_filled_in_my_typical_day, check_version, check_email, generate_otp
from apps.notifications.models import UserDevice 
from apps.admin_app.views import api_logging
from datetime import datetime
from core.encryption import jwt_decode_handler


def check_phone_number(phone_number):
    try:
        Candidate.objects.get(phone__iexact=phone_number, active=True)
        raise exceptions.ValidationError(message_response(user_phone_exists), 400)
    except ObjectDoesNotExist:
        pass


def check_language(candidate, language):
    try:
        CandidateLanguage.objects.get(candidate=candidate, language=language, active=True)
        raise exceptions.ValidationError(message_response(language_exists), 400)
    except ObjectDoesNotExist:
        pass

# def get_relevant_exp(user):
#     user_total_experiences = EmploymentDetail.objects.filter(candidate=user, active=True)
#     total_experience = 0
#     relevant_exp_dict = {}
#     start = None
#     date_list = []
#     total_exp = 0
#     years_of_break = 0
#     for each_exp in user_total_experiences:
#         date_list.append(str(each_exp.start_date))
#         if start and start > str(each_exp.start_date) or not start:
#             start = str(each_exp.start_date)
#         start_date = each_exp.start_date
#         if each_exp.currently_working:
#             date_list.append(str(timezone.now().date()))
#             end_date = parser.parse(str(timezone.now().date()))
#         else:
#             date_list.append(str(each_exp.end_date))
#             end_date = each_exp.end_date
#         rd1 = rdelta.relativedelta(parser.parse(sorted(date_list)[-1]), parser.parse(start))
#         total_employment = float("{0.years}.{0.months}".format(rd1))
#         rd = rdelta.relativedelta(end_date, start_date)
#         role_id = 'r' + str(each_exp.role.id)
#         exp = float("{0.years}.{0.months}".format(rd))
#         total_exp += exp
#         relevant_exp = relevant_exp_dict.get(role_id, 0) + exp
#         relevant_exp_dict.update({role_id: relevant_exp})
#         total_experience += exp
#         print('tot-', total_employment, 'exp-', total_exp)
#         years_of_break = total_employment - total_exp
#     user.years_of_break = round(years_of_break, 2)
#     user.total_year_of_experience = round(total_experience, 2)
#     user.relevantexp.update(relevant_exp_dict)
#     user.save()
#     return True

def update_role(user):
    roles = list(EmploymentDetail.objects.filter(active=True, candidate=user).values_list('role__id', flat=True).
                 distinct('role__id'))
    user.roles.set(roles)
    user.profile_last_updated = timezone.now()
    user.save()
    return True


# def check_dates_range(request, employment):
#     start = None
#     end = None
#     # dates = list()
#     a = 0
#     while a <=len(employment):
#         for employment in employment:
#             print('hi')
#             start = str(employment.start_date)
#             if not employment.end_date:
#                 end = str(timezone.now().date())
#             else:
#                 end = str(employment.end_date)
#             # if request.data['start_date'] in range(start, end):
#             #     print('sdfghj')
#             if start <= request.data['start_date'] <= end or \
#                     end <= request.data['start_date'] <= start:
#                 return Response(message_response(check_dates), 400)
#             elif end <= request.data['end_date'] <= start or \
#                     start <= request.data['end_date'] <= end:
#                 return Response(message_response(check_dates), 400)
#             else:
#                 a +=1
#             # dates.append(str(employment.start_date))
#             # if not employment.currently_working:
#             #     dates.append(str(employment.end_date))
#             # print(dates)
#         # if 'id' in request.data and request.data['id'] != employment.id:
#         #     if employment.currently_working and request.data['currently_working']:
#         #         return Response(message_response(currently_working), 400)
#         #     if str(employment.start_date) <= request.data['start_date'] <= str(employment.end_date):
#         #         return Response(message_response(check_dates), 400)
#         #     if str(employment.end_date) <= request.data['end_date'] <= str(employment.start_date):
#         #         return Response(message_response(check_dates), 400)
#         return True


def check_dates_overlap(user, start, end, update_id=None):
    full_time_query = EmploymentDetail.objects.filter(active=True, candidate=user,
                                                      employment_type__in=['Full Time Employee',
                                                                           'Full Time Contractor'])
    if update_id:
        full_time_query = full_time_query.exclude(id=update_id)
    if end is None:
        check = full_time_query.filter(Q(currently_working=True) | Q(end_date__gte=start))
    else:
        check = full_time_query.filter(Q(start_date__lte=end, end_date__gte=start) |
                                       Q(start_date__lte=end, currently_working=True))
    return check.exists()


def check_candidate_answered_all_question(lifestyle_response):
    """
        check candidate answered all question or not
        Removing None from lifestyle-response
        return sorted in a lifestyle-response as per questions
    """
    # Remove None from Candidate Lifestyle Response List(is present)
    if None in lifestyle_response:
        lifestyle_response = list(
            filter(lambda item: item is not None, lifestyle_response))

    # Sorting candidate answer choice in ascending order(based on questions)
    lifestyle_response.sort(key=get_question_key)

    # Get the Question answered by Candidate
    questions_answered_by_candidate = list(
        map(get_question_key, lifestyle_response))

    if {'1', '2', '4'}.issubset(set(questions_answered_by_candidate)) or {'1', '2', '3', '4'}.issubset(set(questions_answered_by_candidate)):
        return lifestyle_response
    raise exceptions.ValidationError(message_response(invalid_input), 400)


class CandidateAccountsAPI(ModelViewSet):

    @staticmethod
    @swagger_auto_schema(request_body=SignupSerializer, operation_description='Signup_method: email/phone')
    def candidate_sign_up(request):
        check_version(request)
        signup_method = request.data['signup_method']
        hash_key = request.data.get('hash_key')
        if signup_method == 'email':
            email = str.lower(request.data.get('email'))
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            check_invalid([email, first_name, last_name])
            check_email(email)
        else:
            country_code = request.data.get('country_code')
            phone_number = request.data.get('phone')
            check_invalid([phone_number, country_code])
            check_phone_number(phone_number)
        otp = generate_otp()
        request.data['otp'] = make_password(otp)
        serializer = CandidateSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            if signup_method == 'email':
                subject = 'Email Verification'
                template = 'otp_verification.html'
                recipients = [serializer.data['email']]
                context = {
                    'username': serializer.data['first_name'],
                    "otp": otp
                }
                email_send(subject, template, recipients, context)
            else:
                message = otp + ' is the OTP for verification at FlexiBees. Please use this to verify your phone number for FlexiBees. Do not share your OTP with anyone. ' + hash_key
                send_sms(serializer.data['country_code'], serializer.data['phone'], message)
            candidate_obj = Candidate.objects.get(id=serializer.data['id'])
            candidate_obj.active = False
            candidate_obj.save()
            return Response({'user_id': candidate_obj.id, 'hash_key': hash_key})
        return Response(serializer.errors, status=400)

    @staticmethod
    @swagger_auto_schema(request_body=VerifyOTPSerializer)
    def verify_otp(request):
        user_id = request.data.get('user_id', None)
        otp = request.data.get('otp', None)
        check_invalid([user_id, otp])
        if user_id in APPTEST_USERID and otp == '1234':
           user = Candidate.objects.get(id=user_id)
        else:
           user = candidate_verify_otp(user_id, otp)
        if not user:
            return Response(message_response(verification_failed), status=400)
        user.password = make_password(otp)
        user.save()
        payload = jwt_payload_handler(user, 'candidate')
        Candidate.objects.filter(active=True, id=user_id).update(last_login=timezone.now())
        if not user.active:
            if user.email:
                user.email_verified = True
                WebUser.objects.filter(active=True, email=user.email).update(converted=True)
            else:
                user.phone_verified = True
                WebUser.objects.filter(active=True, country_code=user.country_code, phone=user.phone).update(converted=True)
            user.active = True
            user.save()
            subject = 'Welcome to FlexiBees - Complete your Profile to access Flexible Work'
            template = 'signup.html'
            recipients = [user.email]
            context = {
                'username': user.first_name
            }
            push_data = candidate_welcome(user.id)
            send_candidate_notification(users=[user.id], push_data=push_data)
            email_send(subject, template, recipients, context)
        if not user.timeline_completed and user.active and user.questionnaire_completed:
            push_data = candidate_typical_day_notification(user.id)
            send_candidate_notification(users=[user.id], push_data=push_data)
        context = {
            'token': jwt_encode_handler(payload),
            'user': CandidateDetailsSerializer(user).data
        }
        return Response(context)

    @staticmethod
    @swagger_auto_schema(request_body=LoginSerializer)
    def candidate_login(request):
        check_version(request)
        hash_key = request.data.get('hash_key', '')
        if 'email' in request.data:
            email = request.data.get('email')
            check_invalid([email])
            user_obj = get_object_or_404(Candidate, email__iexact=email, active=True)
        else:
            country_code = request.data.get('country_code')
            phone = request.data.get('phone')
            check_invalid([country_code, phone])
            user_obj = get_object_or_404(Candidate, phone__iexact=phone,
                                            country_code__iexact=country_code, active=True)
        otp = generate_otp()
        if 'email' in request.data:
            subject = 'Email Verification'
            template = 'otp_verification.html'
            recipients = [user_obj.email]
            context = {
                'username': user_obj.first_name,
                'otp': otp
            }
            email_send(subject, template, recipients, context)
        else:

            message = otp + ' is the OTP for verification at FlexiBees. Please use this to verify your phone number for FlexiBees. Do not share your OTP with anyone. ' + hash_key
            send_sms(user_obj.country_code, user_obj.phone, message)
        user_obj.otp = make_password(otp)
        user_obj.save()
        return Response({'user_id': user_obj.id, 'hash_key': hash_key})

    @staticmethod
    @swagger_auto_schema(request_body=LoginSerializer)
    def resend_otp(request):
        hash_key = request.data.get('hash_key', '')
        type = request.data.get('sign_up', None)
        id = request.data.get('user_id', None)
        check_invalid([id])
        try:
            user_id =  jwt_decode_handler(id)['ai']
        except:
            return Response(message_response(something_went_wrong))
        if 'email' in request.data:
            email = request.data.get('email')
            check_invalid([email])
            user_obj = get_object_or_404(Candidate, id=user_id, email__iexact=email)
        else:
            country_code = request.data.get('country_code')
            phone = request.data.get('phone')
            check_invalid([country_code, phone])
            user_obj = get_object_or_404(Candidate, id=user_id, phone__iexact=phone, country_code__iexact=country_code)
        otp = generate_otp()
        if user_obj:
            if 'email' in request.data:
                subject = 'Email Verification'
                template = 'otp_verification.html'
                recipients = [user_obj.email]
                context = {
                    'username': user_obj.first_name,
                    "otp": otp
                }
                email_send(subject, template, recipients, context)
            else:
                message = otp + ' is the OTP for verification at FlexiBees. Please use this to verify your phone number for FlexiBees. Do not share your OTP with anyone. ' + hash_key
                send_sms(user_obj.country_code, user_obj.phone, message)
            if type and type!='sign_up':
                return Response(message_response(something_went_wrong))
            elif type=='sign_up' and 'email' in request.data:
                user_obj.password = make_password(otp)
            else:
                user_obj.otp = make_password(otp)
            user_obj.save()
            return Response({'user_id': user_obj.id, 'hash_key': hash_key})
        else:
            return Response(message_response(user_does_not_exist), 404)


class CandidateEmailPhoneVerifyAPI(ModelViewSet):
    permission_classes = (AppUserAuthentication, AppVersionPermission,)

    @staticmethod
    @swagger_auto_schema(request_body=LoginSerializer, operation_description='verify_type: email/phone')
    def candidate_email_phone_verify(request):
        hash_key = request.data.get('hash_key')
        verify_type = request.data['verify_type']
        if verify_type == 'email':
            if request.user.email:
                return Response (message_response(already_email_verified))
            email = str.lower(request.data.get('email'))
            check_invalid([email])
            candidate_obj = Candidate.objects.filter(~Q(id=request.user.id), email__iexact=email, active=True)
        else:
            country_code = request.data.get('country_code')
            phone_number = request.data.get('phone')
            check_invalid([phone_number, country_code])
            candidate_obj = Candidate.objects.filter(~Q(id=request.user.id), phone__iexact=phone_number,
                                                        country_code__iexact=country_code, active=True)
        if candidate_obj:
            return Response(message_response(user_exist), 400)
        otp = generate_otp()
        if verify_type == 'email':
            subject = 'Email Verification'
            template = 'otp_verification.html'
            recipients = [request.data.get('email')]
            context = {
                'username': request.user.first_name,
                "otp": otp
            }
            email_send(subject, template, recipients, context)
        else:
            message = otp + ' is the OTP for verification at FlexiBees. Please use this to verify your phone number for FlexiBees. Do not share your OTP with anyone. ' + hash_key
            send_sms(request.data.get('country_code'), request.data.get('phone'), message)
        request.user.otp = make_password(otp)
        request.user.save()
        return Response({'user_id': request.user.id, 'hash_key': hash_key})

    @staticmethod
    @swagger_auto_schema(request_body=VerifyOTPSerializer, operation_description='verify_type: email/phone')
    def candidate_otp_verify(request):
        verify_type = request.data['verify_type']
        user_id = request.data.get('user_id', None)
        otp = request.data.get('otp', None)
        is_latest_version = request.data.get("is_latest_version", 0)
        if is_latest_version == 1:
            if verify_type == 'email':
                email = str.lower(request.data.get('email'))
                check_invalid([email])
                candidate_obj = Candidate.objects.filter(~Q(id=request.user.id), email__iexact=email, active=True)
            else:
                country_code = request.data.get('country_code')
                phone_number = request.data.get('phone')
                check_invalid([phone_number, country_code])
                candidate_obj = Candidate.objects.filter(~Q(id=request.user.id), phone__iexact=phone_number,
                                                        country_code__iexact=country_code, active=True)
            if candidate_obj:
                return Response(message_response(user_exist), 400)
        check_invalid([user_id, otp])
        user = get_object_or_404(Candidate, id=request.user.id)
        candidate_email = user.email
        if not user.check_otp(otp):
            return Response(message_response(verification_failed), 400)
        if verify_type == 'email':
            user.email_verified = True
            if is_latest_version == 1:
                user.email = request.data['email']
        else:
            user.phone_verified = True
            if is_latest_version == 1:
                user.country_code = request.data['country_code']
                user.phone = request.data['phone']
        user.save()
        if verify_type == 'email':
            if user.email != candidate_email and is_latest_version == 1: 
                subject = 'Welcome to FlexiBees - Complete your Profile to access Flexible Work'
                template = 'email_verified.html'
                recipients = [user.email]
                context = {
                        'username': user.first_name,
                        'email_content': 'Thank you for registering your new email id with FlexiBees.' if candidate_email else 'Thank you for registering your email with FlexiBees.'
                    } 
                email_send(subject, template, recipients, context)
            return Response(message_response(email_verified), 200)
        return Response(message_response(phone_verified), 200)


class CandidateProfileAPI(ModelViewSet):
    permission_classes = (AppUserAuthentication, AppVersionPermission,)

    @staticmethod
    @swagger_auto_schema(request_body=CandidateProfileSerializer)
    def candidate_profile_update(request):
        is_latest_version = request.data.get("is_latest_version", 0)
        candidate_query = get_object_or_404(Candidate, id=request.user.id, active=True)
        candidate_email = candidate_query.email
        request.data['profile_last_updated'] = timezone.now()
        serializers = CandidateProfileSerializer(candidate_query, data=request.data, partial=True)
        candidate_obj = None
        if 'phone' in request.data and 'country_code' in request.data:
            candidate_obj = Candidate.objects.filter(~Q(id=request.user.id), phone__iexact=request.data.get('phone'),
                                                     country_code__iexact=request.data.get('country_code'), active=True)
        if 'email' in request.data:
            candidate_obj = Candidate.objects.filter(~Q(id=request.user.id), email__iexact=request.data.get('email'),
                                                     active=True)
        if candidate_obj:
            return Response(message_response(cannot_update_profile), 400)
        if serializers.is_valid():
            serializers.save()
            email = request.data.get('email',None)
            if email and email != candidate_email and not is_latest_version: 
                subject = 'Welcome to FlexiBees - Complete your Profile to access Flexible Work'
                template = 'email_verified.html'
                recipients = [email]
                context = {
                        'username': candidate_query.first_name,
                        'email_content': 'Thank you for registering your new email id with FlexiBees.' if candidate_email else 'Thank you for registering your email with FlexiBees.'
                    } 
                email_send(subject, template, recipients, context)
            if candidate_email and email and email != candidate_email:
                    candidate_query.previous_email = candidate_email
                    candidate_query.save()
            new_serializers = CandidateDetailsSerializer(Candidate.objects.filter(id=serializers.data['id'], active=True)[0])
            return Response(new_serializers.data)
        return Response(serializers.errors, 400)

    @staticmethod
    def view_candidate_profile(request):
        candidate_query = get_object_or_404(Candidate, id=request.user.id, active=True)
        serializers = CandidateBasicProfileViewSerializer(candidate_query)
        return Response(serializers.data)

    @staticmethod
    def delete_candidate_profile(request):
        candidate_query = get_object_or_404(Candidate, id=request.user.id, active=True)
        final_selection = FinalSelection.objects.filter(candidate=candidate_query.id, active=True).\
            exclude(project__status__in=[9, 10, 11]).exclude(status__in=[3, 4, 6])
        request.role = 'candidate'
        # On Behalf of Candidate Super-Admin will inform Admins about the Deletion Request.
        sent_by_super_admin = get_object_or_404(AdminUser, roles=SUPER_ADMIN_ROLE, email=SUPER_ADMIN_EMAIL, active=True)
        message_1 = "Hi, {candidate_name} candidate who is in the final selection stage of {client_name}, {role_name} wants to delete her profile. Kindly reach out to her to address her concerns."
        message_2 = "Hi, the candidate named {candidate_name}, who is in {client_role_str}, has deleted her profile. You will not be able to move the candidate further because of this."
        message_3 = "Hi, the candidate named {candidate_name}, who is in {client_role_str}, recruitment process has deleted her profile."
        message_4 = "Hi, the candidate named {candidate_name}, who is not part of any recruitment process has deleted her profile."
        candidate_name = f"{candidate_query.first_name} {candidate_query.last_name}"
        if final_selection.exists():
            for final_selection_obj in final_selection:
                recruiter_message = message_1.format(candidate_name=candidate_name, client_name=final_selection_obj.project.company_name, role_name=final_selection_obj.project.role.tag_name)
                # Notify recruiters
                notify_admin(item_type=ITEM_TYPE_CANDIDATE, item_id=candidate_query.id, sent_by=sent_by_super_admin,
                             sent_by_type=request.role, sent_to_type=SENT_TO_TYPE_RECRUITER, message=recruiter_message,
                             sent_to=final_selection_obj.project.recruiter)
            return Response(message_response(cannot_delete_profile), 400)
        candidate_query.active = False
        candidate_query.save()
        shortlist_query = list(Shortlist.objects.filter(active=True, candidate=candidate_query.id,
                                                        status=2).values_list('project', flat=True))
        interest_check_and_self_evaluation_query = list(InterestCheckAndSelfEvaluation.objects.filter(
            active=True, candidate=candidate_query.id, status__in=[1, 2]).values_list('project', flat=True))
        assignment_query = list(Assignment.objects.filter(active=True, candidate=candidate_query.id).values_list(
            'project', flat=True))
        functional_query = list(Functional.objects.filter(active=True, candidate=candidate_query.id).values_list(
            'project', flat=True))
        flexifit_query = list(Flexifit.objects.filter(active=True, candidate=candidate_query.id).values_list('project',
                                                                                                             flat=True))
        projects_list = list(set(shortlist_query + interest_check_and_self_evaluation_query + assignment_query + functional_query + \
                        flexifit_query))
        list_of_client_name_role = [] 
        # Notify recruiters if project status is not closed, suspended, and reopened [9, 10, 11].
        for project in projects_list:
            project_query = get_object_or_404(Project, id=project, active=True)
            if project_query.status not in [9, 10, 11]:
                company_role = (project_query.company_name, project_query.role.tag_name)
                list_of_client_name_role.append(company_role)
                recruiter_message = message_2.format(candidate_name=candidate_name, client_role_str=", ".join(company_role))
                notify_admin(item_type=ITEM_TYPE_CANDIDATE, item_id=candidate_query.id, sent_by=sent_by_super_admin, sent_by_type=request.role,
                            sent_to_type=SENT_TO_TYPE_RECRUITER, message=recruiter_message, sent_to=project_query.recruiter)
          
        clint_name_role_str = ', '.join(map('-'.join, list_of_client_name_role)) if len(list_of_client_name_role) else None
        # Notify Super Admin
        notify_admin(item_type=ITEM_TYPE_CANDIDATE, item_id=candidate_query.id, sent_by=sent_by_super_admin,
                        sent_by_type=request.role, sent_to_type=SENT_TO_TYPE_SUPER_ADMIN, message=message_3.format(candidate_name=candidate_name, client_role_str=clint_name_role_str) if clint_name_role_str else message_4.format(candidate_name=candidate_name))
        # Notify recruiter admins
        notify_admin(item_type=ITEM_TYPE_CANDIDATE, item_id=candidate_query.id, sent_by=sent_by_super_admin, sent_by_type=request.role,
                     sent_to_type=SENT_TO_TYPE_RECRUITER_ADMIN, message=message_2.format(candidate_name=candidate_name, client_role_str=clint_name_role_str) if clint_name_role_str else message_4.format(candidate_name=candidate_name))
        return Response(message_response(deleted), 200)

    @staticmethod
    def candidate_profile(request):
        candidate_query = get_object_or_404(Candidate, id=request.user.id, active=True)
        serializers = CandidateProfileViewSerializer(candidate_query)
        return Response(serializers.data)

    @staticmethod
    @swagger_auto_schema(request_body=CandidateWorkExperienceSerializer)
    def candidate_work_experience_update(request):
        candidate_query = get_object_or_404(Candidate, id=request.user.id, active=True)
        if 'id' in request.data:
            employment_detail = get_object_or_404(EmploymentDetail, active=True, id=request.data['id'], candidate=candidate_query.id)
            if request.data['employment_type'] in ['Full Time Employee', 'Full Time Contractor'] and \
                    check_dates_overlap(candidate_query, request.data['start_date'], request.data.get('end_date'),
                                        update_id=request.data['id']):
                return Response(message_response(check_dates), status=400)
            serializers = CandidateWorkExperienceSerializer(employment_detail, data=request.data, partial=True)
        elif request.data['employment_type'] in ['Full Time Employee', 'Full Time Contractor'] and \
                    check_dates_overlap(candidate_query, request.data['start_date'], request.data.get('end_date')):
            return Response(message_response(check_dates), status=400)
        else:
            serializers = CandidateWorkExperienceSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            # update_role(request.user)
            # get_relevant_exp(candidate_query)
            new_serializers = CandidateWorkExperienceViewSerializer(EmploymentDetail.objects.filter(active=True, id=serializers.data['id'])[0])
            return Response(new_serializers.data)
        return Response(serializers.errors, 400)

    @staticmethod
    def view_candidate_work_experience(request):
        candidate_query = get_object_or_404(Candidate, id=request.user.id, active=True)
        employment_detail_query = EmploymentDetail.objects.filter(active=True, candidate=candidate_query.id)
        serializers = CandidateWorkExperienceViewSerializer(employment_detail_query, many=True)
        return Response(serializers.data)

    @staticmethod
    def delete_candidate_work_experience(request, work_experience):
        employment_detail_query = get_object_or_404(EmploymentDetail, active=True, id=work_experience, candidate=request.user)
        employment_detail_query.active = False
        employment_detail_query.save()
        # update_role(request.user)
        # get_relevant_exp(employment_detail_query.candidate)
        return Response(message_response(deleted), 200)

    @staticmethod
    @swagger_auto_schema(request_body=CandidateEducationSerializer)
    def candidate_education_update(request):
        candidate_query = get_object_or_404(Candidate, id=request.user.id, active=True)
        if 'id' in request.data:
            education_query = get_object_or_404(Education, active=True, id=request.data['id'], candidate=candidate_query.id)
            serializers = CandidateEducationSerializer(education_query, data=request.data, partial=True)
        else:
            request.data['candidate'] = candidate_query.id
            serializers = CandidateEducationSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            request.user.profile_last_updated = timezone.now()
            request.user.save()
            new_serializers = CandidateEducationViewSerializer(Education.objects.filter(active=True, id=serializers.data['id'])[0])
            return Response(new_serializers.data)
        return Response(serializers.errors, 400)

    @staticmethod
    def view_candidate_education(request):
        candidate_query = get_object_or_404(Candidate, id=request.user.id, active=True)
        education_query = Education.objects.filter(active=True, candidate=candidate_query.id)
        serializers = CandidateEducationViewSerializer(education_query, many=True)
        return Response(serializers.data)

    @staticmethod
    def delete_candidate_education(request, education):
        education_query = get_object_or_404(Education, active=True, id=education, candidate=request.user)
        education_query.active = False
        request.user.profile_last_updated = timezone.now()
        education_query.save()
        request.user.save()
        return Response(message_response(deleted), 200)

    @staticmethod
    @swagger_auto_schema(request_body=CandidateCertificationSerializer)
    def candidate_certification_update(request):
        candidate_query = get_object_or_404(Candidate, id=request.user.id, active=True)
        if 'id' in request.data:
            certification_query = get_object_or_404(Certification, active=True, id=request.data['id'], candidate=candidate_query.id)
            serializers = CandidateCertificationSerializer(certification_query, data=request.data, partial=True)
        else:
            request.data['candidate'] = candidate_query.id
            serializers = CandidateCertificationSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            request.user.profile_last_updated = timezone.now()
            request.user.save()
            new_serializers = CandidateCertificationViewSerializer(Certification.objects.filter(active=True, id=serializers.data['id'])[0])
            return Response(new_serializers.data)
        return Response(serializers.errors, 400)

    @staticmethod
    def view_candidate_certification(request):
        candidate_query = get_object_or_404(Candidate, id=request.user.id, active=True)
        certification_query = Certification.objects.filter(active=True, candidate=candidate_query.id)
        serializers = CandidateCertificationViewSerializer(certification_query, many=True)
        return Response(serializers.data)

    @staticmethod
    def delete_candidate_certification(request, certification):
        certification_query = get_object_or_404(Certification, active=True, id=certification, candidate=request.user)
        certification_query.active = False
        certification_query.save()
        request.user.profile_last_updated = timezone.now()
        request.user.save()
        return Response(message_response(deleted), 200)

    @staticmethod
    @swagger_auto_schema(request_body=CandidateLanguageSerializer)
    def candidate_language_update(request):
        candidate_query = get_object_or_404(Candidate, id=request.user.id, active=True)
        if 'id' in request.data:
            candidate_language_query = get_object_or_404(CandidateLanguage, active=True, id=request.data['id'],
                                                         candidate=candidate_query.id)
            serializers = CandidateLanguageSerializer(candidate_language_query, data=request.data, partial=True)
            if candidate_language_query.language.id != request.data['language']:
                check_language(candidate_query, request.data['language'])
        else:
            check_language(candidate_query, request.data['language'])
            request.data['candidate'] = candidate_query.id
            serializers = CandidateLanguageSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            request.user.profile_last_updated = timezone.now()
            request.user.save()
            new_serializers = CandidateLanguageViewSerializer(CandidateLanguage.objects.filter(active=True, id=serializers.data['id'])[0])
            return Response(new_serializers.data)
        return Response(serializers.errors, 400)

    @staticmethod
    def view_candidate_language(request):
        candidate_query = get_object_or_404(Candidate, id=request.user.id, active=True)
        candidate_language_query = CandidateLanguage.objects.filter(candidate=candidate_query.id, active=True)
        serializers = CandidateLanguageViewSerializer(candidate_language_query, many=True)
        return Response(serializers.data, 200)

    @staticmethod
    def delete_candidate_language(request, language):
        candidate_language_query = get_object_or_404(CandidateLanguage, id=language, active=True, candidate=request.user)
        candidate_language_query.active = False
        candidate_language_query.save()
        request.user.profile_last_updated = timezone.now()
        request.user.save()
        return Response(message_response(deleted), 200)

    @staticmethod
    @swagger_auto_schema(request_body=CandidateAttachmentSerializer)
    def candidate_attachment_update(request):
        candidate_query = get_object_or_404(Candidate, id=request.user.id, active=True)
        serializers = CandidateAttachmentSerializer(candidate_query.candidateattachment_set.get_or_create(active=True)[0], data=request.data,
                                                    partial=True)
        if serializers.is_valid():
            serializers.save()
            request.user.profile_last_updated = timezone.now()
            request.user.save()
            new_serializers = CandidateAttachmentViewSerializer(CandidateAttachment.objects.get(active=True, id=serializers.data['id']))
            return Response(new_serializers.data)
        return Response(serializers.errors, 400)

    @staticmethod
    def view_candidate_attachment(request):
        candidate_query = get_object_or_404(Candidate, id=request.user.id, active=True)
        candidate_attachment_query = get_object_or_404(CandidateAttachment, candidate=candidate_query.id, active=True)
        serializers = CandidateAttachmentViewSerializer(candidate_attachment_query)
        return Response(serializers.data, 200)

    @staticmethod
    def delete_candidate_attachment(request):
        candidate_query = get_object_or_404(Candidate, id=request.user.id, active=True)
        candidate_attachment_query = get_object_or_404(CandidateAttachment, candidate=candidate_query.id, active=True)
        candidate_attachment_query.active = False
        candidate_attachment_query.save()
        request.user.profile_last_updated = timezone.now()
        request.user.save()
        return Response(message_response(deleted), 200)

    @staticmethod
    @swagger_auto_schema(request_body=CandidateOtherDetailsSerializer)
    def candidate_other_details_update(request):
        candidate_query = get_object_or_404(Candidate, id=request.user.id, active=True)
        request.data['profile_last_updated'] = timezone.now()
        serializers = CandidateOtherDetailsSerializer(candidate_query, data=request.data, partial=True)
        if serializers.is_valid():
            serializers.save()
            new_serializers = CandidateOtherDetailsViewSerializer(candidate_query)
            return Response(new_serializers.data)
        return Response(serializers.errors, 400)

    @staticmethod
    def view_candidate_other_details(request):
        candidate_query = get_object_or_404(Candidate, id=request.user.id, active=True)
        serializers = CandidateOtherDetailsViewSerializer(candidate_query)
        return Response(serializers.data, 200)

    @staticmethod
    def delete_candidate_other_details(request):
        candidate_query = get_object_or_404(Candidate, id=request.user.id, active=True)
        request.data['profile_last_updated'] = timezone.now()
        serializers = CandidateOtherDetailsSerializer(candidate_query, data=request.data, partial=True)
        if serializers.is_valid():
            serializers.save()
            return Response(message_response(deleted), 200)
        return Response(serializers.errors, 400)


class CandidateProjectHistoryAPI(ModelViewSet):
    permission_classes = (AppUserAuthentication, AppVersionPermission,)

    @staticmethod
    def candidate_project_history(request):
        candidate_query = get_object_or_404(Candidate, active=True, id=request.user.id)
        shortlist_query = list(Shortlist.objects.filter(active=True, candidate=candidate_query.id,
                                                        status=2).values_list('project', flat=True))
        interest_check_and_self_evaluation_query = list(InterestCheckAndSelfEvaluation.objects.filter(
            active=True, candidate=candidate_query.id, status__in=[1, 2]).values_list('project', flat=True))
        assignment_query = list(Assignment.objects.filter(active=True, candidate=candidate_query.id, status__in=[3, 5]).
                                values_list('project', flat=True).order_by('-modified'))
        functional_query = list(Functional.objects.filter(active=True, candidate=candidate_query.id, status__in=[3, 4]).
                                values_list('project', flat=True).order_by('-modified'))
        flexifit_query = list(Flexifit.objects.filter(active=True, candidate=candidate_query.id, status__in=[3, 4]).
                              values_list('project', flat=True).order_by('-modified'))
        final_selection_query = list(FinalSelection.objects.filter(
            active=True, candidate=candidate_query.id, status__in=[1, 2, 3, 5]).values_list('project', flat=True).order_by('-modified'))
        final_selection_query1 = list(FinalSelection.objects.filter(
            active=True, candidate=candidate_query.id, status__in=[4, 6]).values_list('project', flat=True).order_by('-modified'))
        project_ids = list(set(assignment_query + functional_query + flexifit_query + shortlist_query +
                               interest_check_and_self_evaluation_query + final_selection_query))
        projects_query = Project.objects.filter(active=True)
        project_ids = list(projects_query.filter(id__in=project_ids, active=True, status__in=[9, 11]).values_list('id', flat=True))
        project_ids = list(set(final_selection_query1 + project_ids))
        project_query = projects_query.filter(id__in=project_ids, active=True).order_by('-modified')
        serializers = ProjectListingSerializer(project_query, many=True)
        for project in serializers.data:
            if project['id'] in shortlist_query:
                model = getattr(candidate.models, "Shortlist")
                status_reference = 'Shortlist'
            elif project['id'] in interest_check_and_self_evaluation_query:
                model = getattr(candidate.models, "InterestCheckAndSelfEvaluation")
                status_reference = 'InterestCheckAndSelfEvaluation'
            elif project['id'] in assignment_query:
                model = getattr(candidate.models, "Assignment")
                status_reference = 'Assignment'
            elif project['id'] in functional_query:
                model = getattr(candidate.models, "Functional")
                status_reference = 'Functional'
            elif project['id'] in flexifit_query:
                model = getattr(candidate.models, "Flexifit")
                status_reference = 'Flexifit'
            elif project['id'] in (final_selection_query + final_selection_query1):
                model = getattr(candidate.models, "FinalSelection")
                status_reference = 'FinalSelection'
            else:
                model = None
                status_reference = None
            obj = model.objects.filter(project=project['id'], candidate=candidate_query.id, active=True)
            project_obj = get_object_or_404(Project, id=project['id'], active=True)
            project['status'] = obj[0].status
            project['modified'] = project_obj.modified
            project['status_reference'] = status_reference
            project['project_details']['candidate_hired_date'] = None
            final_selection_obj = FinalSelection.objects.filter(project=project['id'], candidate=request.user.id,
                                                                status=3, active=True)
            if final_selection_obj:
                client_feedback_obj = ClientFeedback.objects.filter(final_selection=final_selection_obj[0].id,
                                                                    recommendation=3, active=True)
                project['project_details']['candidate_hired_date'] = client_feedback_obj[
                    0].modified if client_feedback_obj else None
        return Response(serializers.data)


class CandidateActiveProjectsAPI(ModelViewSet):
    permission_classes = (AppUserAuthentication, AppVersionPermission,)

    @staticmethod
    def candidate_active_projects(request):
        # active projects api is linked in home page and candidate journey apis 
        try:
            is_latest_version = int(request.GET.get('is_latest_version', 0))
        except:
            is_latest_version = 0
        if is_latest_version == 1 :
            is_my_typical_day_updated = min_hours_filled_in_my_typical_day(request.user.id)
        try:
            candidate_query = get_object_or_404(Candidate, active=True, id=request.user.id)
        except:
            candidate_query = get_object_or_404(Candidate, active=True, id=request.id)
        shortlist_query = list(Shortlist.objects.filter(active=True, candidate=candidate_query.id, candidate__hire=True,
                                                        status=2).values('project', 'modified'))
        shortlist_projects = [sub['project'] for sub in shortlist_query]
        interest_check_and_self_evaluation_query = list(InterestCheckAndSelfEvaluation.objects.filter(
            active=True, candidate=candidate_query.id, status__in=[1, 2], candidate__hire=True).values('project', 'modified'))
        interest_check_and_self_evaluation_projects = [sub['project'] for sub in interest_check_and_self_evaluation_query]
        assignment_query = list(Assignment.objects.filter(
            active=True, candidate=candidate_query.id, candidate__hire=True).values('project', 'modified'))
        assignment_projects = [sub['project'] for sub in assignment_query]
        if is_latest_version==1 and not is_my_typical_day_updated:
            cleared_functional_ids = list(Functional.objects.filter(
            active=True, candidate=candidate_query.id, candidate__hire=True, status=2).order_by('-modified').values_list('project',flat=True))
        functional_query = list(Functional.objects.filter(
            active=True, candidate=candidate_query.id, candidate__hire=True).values('project', 'modified'))
        functional_projects = [sub['project'] for sub in functional_query]
        flexifit_query = list(Flexifit.objects.filter(
            active=True, candidate=candidate_query.id, candidate__hire=True).values('project', 'modified'))
        flexifit_projects = [sub['project'] for sub in flexifit_query]
        final_selection_query = list(FinalSelection.objects.filter(
            active=True, candidate=candidate_query.id, candidate__hire=True, status__in=[1, 2, 3, 5]).values('project', 'modified'))
        final_selection_projects = [sub['project'] for sub in final_selection_query]
        projects_list = shortlist_query + interest_check_and_self_evaluation_query + assignment_query+functional_query + \
                        flexifit_query + final_selection_query
        result = set()
        result_list = [x for x in projects_list if [x['project'] not in result, result.add(x['project'])][0]]
        new_list = sorted(result_list, reverse=True, key=lambda k: k['modified'])
        project_ids = [sub['project'] for sub in new_list]
        # showing functional projects on top if candidate not updated my life and my typical day
        if is_latest_version==1 and not is_my_typical_day_updated:
            project_ids = cleared_functional_ids + [x for x in project_ids if x not in cleared_functional_ids]
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(project_ids)])
        project_query = Project.objects.filter(id__in=project_ids, active=True).exclude(status__in=[9, 11]).order_by(preserved)
        serializers = ProjectListingSerializer(project_query, many=True)
        for project in serializers.data:
            if project['id'] in shortlist_projects:
                model = getattr(candidate.models, "Shortlist")
                status_reference = 'Shortlist'
            elif project['id'] in interest_check_and_self_evaluation_projects:
                model = getattr(candidate.models, "InterestCheckAndSelfEvaluation")
                status_reference = 'InterestCheckAndSelfEvaluation'
            elif project['id'] in assignment_projects:
                model = getattr(candidate.models, "Assignment")
                status_reference = 'Assignment'
            elif project['id'] in functional_projects:
                model = getattr(candidate.models, "Functional")
                status_reference = 'Functional'
            elif project['id'] in flexifit_projects:
                model = getattr(candidate.models, "Flexifit")
                status_reference = 'Flexifit'
            elif project['id'] in final_selection_projects:
                model = getattr(candidate.models, "FinalSelection")
                status_reference = 'FinalSelection'
            else:
                model = None
                status_reference = None
            obj = model.objects.filter(project=project['id'], candidate=candidate_query.id, active=True)
            try:
                assignment_obj = Assignment.objects.filter(project=project['id'], candidate=request.user.id, active=True)
            except:
                assignment_obj = Assignment.objects.filter(project=project['id'], candidate=request.id, active=True)
            project['status'] = obj[0].status
            project['modified'] = obj[0].modified
            project['status_reference'] = status_reference
            project['project_details']['assignment_due_date'] = assignment_obj[0].due_date if assignment_obj else None
        if is_latest_version == 1 :
            context = {
                'results' : serializers.data,
                'total_results':len(serializers.data)
            }
            if len(list(functional_query)) :
                context['candidate_details'] ={
                    'is_my_life_updated' : bool(request.user.lifestyle_responses),
                    'is_typical_day_updated' : is_my_typical_day_updated
                }
        return Response(context if is_latest_version==1 else serializers.data)
    

class ProjectDetailsAPI(ModelViewSet):
    permission_classes = (AppUserAuthentication, AppVersionPermission,)

    @staticmethod
    def project_details(request, project):
        if request.user.hire == False:
            return Response(message_response(cannot_access_project_details_for_not_hire), 400)
        project_query = get_object_or_404(Project, active=True, id=project)
        serializers = ProjectDetailSerializer( project_query)
        shortlist_query = Shortlist.objects.filter(active=True, candidate=request.user.id, project=serializers.data['id'])
        interest_check_and_self_evaluation_query = InterestCheckAndSelfEvaluation.objects.filter(
            active=True, candidate=request.user.id, project=serializers.data['id'])
        assignment_query = Assignment.objects.filter(active=True, candidate=request.user.id, project=serializers.data['id'])
        functional_query = Functional.objects.filter(active=True, candidate=request.user.id, project=serializers.data['id'])
        flexifit_query = Flexifit.objects.filter(active=True, candidate=request.user.id, project=serializers.data['id'])
        final_selection_query = FinalSelection.objects.filter(active=True, candidate=request.user.id, project=serializers.data['id'])
        project_count = len(list(shortlist_query) + list(interest_check_and_self_evaluation_query) + list(assignment_query) + list(functional_query) + list(flexifit_query) + list(final_selection_query))
        if not project_count :
            return Response(message_response(cannot_access_project_details), 400)
        serializers.data['project_details']['status'] = None
        serializers.data['project_details']['status_reference'] = None
        if shortlist_query:
            serializers.data['project_details']['status'] = shortlist_query[0].status
            serializers.data['project_details']['status_reference'] = "Shortlist"
        if interest_check_and_self_evaluation_query:
            serializers.data['project_details']['status'] = interest_check_and_self_evaluation_query[0].status
            serializers.data['project_details']['status_reference'] = "InterestCheckAndSelfEvaluation"
        if assignment_query:
            serializers.data['project_details']['status'] = assignment_query[0].status
            serializers.data['project_details']['status_reference'] = "Assignment"
        if functional_query:
            serializers.data['project_details']['status'] = functional_query[0].status
            serializers.data['project_details']['status_reference'] = "Functional"
            serializers.data['other_details']['is_my_life_updated'] = bool(request.user.lifestyle_responses)
            serializers.data['other_details']['is_typical_day_updated'] = min_hours_filled_in_my_typical_day(functional_query[0].candidate.id)
            serializers.data['other_details']['is_wakeup_time_updated'] = bool(request.user.wakeup_time)
        if flexifit_query:
            serializers.data['project_details']['status'] = flexifit_query[0].status
            serializers.data['project_details']['status_reference'] = "Flexifit"
        if final_selection_query:
            serializers.data['project_details']['status'] = final_selection_query[0].status
            serializers.data['project_details']['status_reference'] = "FinalSelection"
        serializers.data['project_details']['candidate_hired_date'] = None
        final_selection_obj = FinalSelection.objects.filter(project=serializers.data['id'], candidate=request.user.id,
                                                            status=3, active=True)
        if final_selection_obj:
            client_feedback_obj = ClientFeedback.objects.filter(final_selection=final_selection_obj[0].id,
                                                                recommendation=3, active=True)
            serializers.data['project_details']['candidate_hired_date'] = client_feedback_obj[
                0].created if client_feedback_obj else None
        assignment_obj = Assignment.objects.filter(project=serializers.data['id'], candidate=request.user.id, active=True)
        serializers.data['project_details']['assignment_due_date'] = assignment_obj[0].due_date if assignment_obj else None
        return Response(serializers.data)


class CandidateSkillsAPI(ModelViewSet):
    permission_classes = (AppUserAuthentication, AppVersionPermission,)

    @staticmethod
    def candidate_skills_listing(request):
        search_term = request.data.get('search_term', '')
        if search_term:
            skills_query = Skill.objects.filter(tag_name__icontains=search_term, active=True)
        else:
            skills_query = Skill.objects.filter(active=True)
        serializers = SkillSerializer(skills_query, many=True)
        return Response(serializers.data)


class CandidateRolesAPI(ModelViewSet):
    permission_classes = (AppUserAuthentication, AppVersionPermission,)

    @staticmethod
    def candidate_roles_listing(request):
        search_term = request.data.get('search_term', '')
        if search_term:
            roles_query = Role.objects.filter(tag_name__icontains=search_term, active=True)
        else:
            roles_query = Role.objects.filter(active=True)
        serializers = RoleSerializer(roles_query, many=True)
        return Response(serializers.data)


class CandidateDomainsAPI(ModelViewSet):
    permission_classes = (AppUserAuthentication, AppVersionPermission,)

    @staticmethod
    def candidate_domains_listing(request):
        search_term = request.data.get('search_term', '')
        if search_term:
            domain_query = Domain.objects.filter(tag_name__icontains=search_term, active=True)
        else:
            domain_query = Domain.objects.filter(active=True)
        serializers = DomainSerializer(domain_query, many=True)
        return Response(serializers.data)


class CandidateSupportAPI(ModelViewSet):
    permission_classes = (AppUserAuthentication, AppVersionPermission,)

    @staticmethod
    def candidate_support(request):
        message = request.data.get('message')
        subject = 'Enquiry from App'
        template = 'support.html'
        recipients = ['support@flexibees.com']
        context = {
            'username': request.user.first_name,
            'message': message,
            'email': request.user.email or None,
            'country_code': request.user.country_code,
            'phone': request.user.phone or None,
        }

        email_send(subject, template, recipients, context)
        return Response(message_response(successfully_sent))


class CandidateLanguageAPI(ModelViewSet):
    permission_classes = (AppUserAuthentication, AppVersionPermission,)

    @staticmethod
    def candidate_language_listing(request):
        search_term = request.data.get('search_term', '')
        if search_term:
            language_query = Language.objects.filter(name__icontains=search_term, active=True)
        else:
            language_query = Language.objects.filter(active=True)
        serializers = LanguageSerializer(language_query, many=True)
        return Response(serializers.data)


class CandidateSelfAssessmentAPI(ModelViewSet):
    permission_classes = (AppUserAuthentication, AppVersionPermission,)

    @staticmethod
    def candidate_self_assessment(request, project):
        project_query = get_object_or_404(Project, active=True, id=project)
        must_have_skills = project_query.requirement_set.get_or_create()[0].must_have_skills.all()
        serializers = SkillSerializer(must_have_skills, many=True)
        return Response(serializers.data)

    @staticmethod
    def candidate_self_assessment_update(request, project):
        project_query = get_object_or_404(Project, active=True, id=project)
        candidate_query = get_object_or_404(Candidate, active=True, id=request.user.id)
        request.data['project'] = project_query.id
        request.data['candidate'] = candidate_query.id
        serializers = SelfAssessmentSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            InterestCheckAndSelfEvaluation.objects.filter(active=True, project=project_query.id,
                                                          candidate=candidate_query.id).update(status=2)
            return Response(message_response(self_assessment_completed), 200)
        return Response(serializers.errors, 400)


class CandidateInterestStatusAPI(ModelViewSet):
    permission_classes = (AppUserAuthentication, AppVersionPermission,)

    @staticmethod
    def candidate_interest_status_update(request, project):
        project_query = get_object_or_404(Project, active=True, id=project)
        candidate_query = get_object_or_404(Candidate, active=True, id=request.user.id)
        status = request.data.get('status')
        get, created = InterestCheckAndSelfEvaluation.objects.get_or_create(project=project_query,
                                                             candidate=candidate_query, status=status, active=True)
        if created:
            if status == 3:
                request.user.active_projects -= 1
                request.user.save()
            Shortlist.objects.filter(active=True, project=project_query.id,
                                     candidate=candidate_query.id).update(active=False)
            return Response(message_response(updated), 200)
        return Response(message_response(cannot_update_status), 400)


class CandidateAssignmentAPI(ModelViewSet):
    permission_classes = (AppUserAuthentication, AppVersionPermission,)
    serializer_class = (AssignmentSerializer, )

    @staticmethod
    def candidate_assignment_upload(request, project):
        project_query = get_object_or_404(Project, active=True, id=project)
        candidate_query = get_object_or_404(Candidate, active=True, id=request.user.id)
        assignment_query = get_object_or_404(Assignment, project=project_query.id, candidate=candidate_query.id, active=True)
        request.data['status'] = 2
        request.data['submitted_date'] = timezone.now()
        serializers = AssignmentSerializer(assignment_query, data=request.data, partial=True)
        if serializers.is_valid():
            serializers.save()
            return Response(message_response(assignment_uploaded), 200)
        return Response(serializers.errors, 400)

    @staticmethod
    def view_candidate_assignment(request, project):
        project_query = get_object_or_404(Project, active=True, id=project)
        assignment_query = Assignment.objects.filter(project=project_query.id, candidate=request.user.id, active=True)
        context = {
                'assignment_file': project_query.flexidetails_set.get_or_create()[0].assignment_file,
                'assignment_due_date': assignment_query[0].due_date if assignment_query else None
        }
        return Response(context)


class CandidateInterviewScheduledAPI(ModelViewSet):
    permission_classes = (AppUserAuthentication, AppVersionPermission,)

    @staticmethod
    def view_scheduled_timing(request, project):
        scheduled_for = request.data.get('scheduled_for')
        project_query = get_object_or_404(Project, active=True, id=project)
        candidate_query = get_object_or_404(Candidate, active=True, id=request.user.id)
        if scheduled_for == 'functional':
            functional_query = get_object_or_404(Functional, project=project_query.id, candidate=candidate_query.id)
            serializers = FunctionalInterviewScheduledSerializer(functional_query)
        elif scheduled_for == 'flexifit':
            flexifit_query = get_object_or_404(Flexifit, project=project_query.id, candidate=candidate_query.id)
            serializers = FlexifitInterviewScheduledSerializer(flexifit_query)
        return Response(serializers.data)


class BreakAPI(ModelViewSet):

    def get(self, request, user):
        user_total_experiences = EmploymentDetail.objects.filter(candidate=1, active=True)
        exp_list = []
        total_exp = 0
        years_of_break = 0
        for each_exp in user_total_experiences:
            start = each_exp.start_date
            end = timezone.now().date() if each_exp.currently_working else each_exp.end_date
            exp_list.append({
                'start': start,
                'end': end,
                'role': 'r' + str(each_exp.role.id),
            })
        newlist = sorted(exp_list, key=lambda k: k['start'])
        final_dict = {'total': []}
        for each_item in newlist:
            if each_item['role'] not in final_dict:
                final_dict[each_item['role']] = [[each_item['start'], each_item['end']]]
            else:
                last_role_range = final_dict[each_item['role']][-1]
                if each_item['start'] > last_role_range[1]:
                    final_dict[each_item['role']].append([each_item['start'], each_item['end']])
                else:
                    if each_item['start'] <= last_role_range[0]:
                        last_role_range[0] = each_item['start']
                    if each_item['end'] >= last_role_range[1]:
                        last_role_range[1] = each_item['end']
                    final_dict[each_item['role']][-1] = last_role_range
            if len(final_dict['total']) == 0:
                final_dict['total'].append([each_item['start'], each_item['end']])
            else:
                last_exp_range = final_dict['total'][-1]
                if each_item['start'] > last_exp_range[1]:
                    final_dict['total'].append([each_item['start'], each_item['end']])
                else:
                    if each_item['start'] <= last_exp_range[0]:
                        last_exp_range[0] = each_item['start']
                    if each_item['end'] >= last_exp_range[1]:
                        last_exp_range[1] = each_item['end']
                    final_dict['total'][-1] = last_exp_range
        for a in range(len(final_dict['total'])):
            total_exp += float("{0.years}.{0.months}".format(rdelta.relativedelta(final_dict['total'][a][1],
                                                                                  final_dict['total'][a][0])))
            try:
                years_of_break += float("{0.years}.{0.months}".format(rdelta.relativedelta(final_dict['total'][a+1][0],
                                                                                           final_dict['total'][a][1])))
            except:
                pass
        final_dict.pop('total')
        for b, value in final_dict.items():
            each_role_exp = round(sum(
                float(
                    "{0.years}.{0.months}".format(
                        rdelta.relativedelta(each[1], each[0])
                    )
                )
                for each in value
            ), 2)

            final_dict[b] = each_role_exp
        print(round(total_exp, 2), years_of_break, final_dict)
        return Response(final_dict)


class AppVersionAPI(ModelViewSet):

    @staticmethod
    def get(request):
        latest = AppVersion.objects.filter(active=True).order_by('-id').first()
        context = {
            'android': latest.android,
            'ios': latest.ios,
            'force_update': latest.force_update,
            'recommended_update': latest.recommended_update,
            'under_maintenance': latest.under_maintenance,
            'android_release_note': latest.android_release_note,
            'ios_release_note': latest.ios_release_note
        }
        return Response(context)

    @staticmethod
    @swagger_auto_schema(request_body=AppVersionSerializer)
    def post(request):
        serializers = AppVersionSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data)
        return Response(serializers.errors, 400)


class CandidateLifeStyleAPI(ModelViewSet):
    permission_classes = (AppUserAuthentication, AppVersionPermission,)

    @staticmethod
    def update_lifestyle_response(request):
        candidate_query = get_object_or_404(Candidate, id=request.user.id, active=True)
        lifestyle_responses = request.data.get('lifestyle_responses')
        validation_required = request.data.get('validation_required', 0)
        update_my_typical_day = request.data.get('update_my_typical_day', 1)
        # Only for New mobile app installed versions
        if validation_required == 1:
            lifestyle_responses = check_candidate_answered_all_question(lifestyle_responses)
        if lifestyle_responses:
            candidate_query.lifestyle_responses = lifestyle_responses
            candidate_query.questionnaire_completed = True
            candidate_query.mylife_last_updated = timezone.now()
            candidate_query.last_notified = None
            candidate_query.notification_count = 0
            # Only for Old mobile app versions
            if update_my_typical_day == 1:
                reset_status = reset_typical_day_detail(candidate_query)
                if not reset_status:
                    return Response(message_response(invalid_input), 400)
            candidate_query.save()
            # Check the Wakeup Time of Candidate to find the Typical day section is filled or not.
            context = {
                "message": lifestyle_updated,
                "my_typical_day": 0 if candidate_query.wakeup_time == None else 1
            }
            return Response(context, 200)
        else:
            return Response(message_response(select_one_lifestyle), 400)

    @staticmethod
    def get_lifestyle(request):
        try:
            candidate_obj = get_object_or_404(Candidate, id=request.user.id, active=True)
            
            # Checking Candidate has answered all mandatory Question or Not.
            my_life_status = 1 if get_mylife_status(candidate_obj) == "Yes" else 0

            context, status = {
                "my_life_status" : my_life_status
            }, 200
        except Exception:
            context, status = {
                "message" : not_found
            }, 400
        return Response(context,status)

class CandidateHomePageAPI(ModelViewSet):
    permission_classes = (AppUserAuthentication,)

    @staticmethod
    def candidate_home_page(request):
        is_latest_version = int(request.GET.get('is_latest_version', 0))
        candidate_query = get_object_or_404(Candidate, id=request.user.id, active=True)
        if is_latest_version == 1:
            """
            if the user is already logged in and updates the app through the app store to disable the
            multiple fcm tokens belongs to that user and keep the latest one
            """
            device_type = request.GET.get('type', None)
            registration_id = request.GET.get('registration_id', None)
            try:
                active_device = UserDevice.objects.get(user=request.user, type=device_type, registration_id=registration_id,
                                active=True)
            except:
                check_invalid([device_type, registration_id])
                active_device = UserDevice.objects.create(user=request.user, type=device_type, registration_id=registration_id,
                                        active=True)
            UserDevice.objects.filter(user=request.user, active=True).exclude(id__in=[active_device.id]).update(active=False)
            active_projects = CandidateActiveProjectsAPI.candidate_active_projects(request).data
            candidate_active_projects = active_projects['results'][:2] if len(active_projects['results']) else []
        else:
            candidate_active_projects = CandidateActiveProjectsAPI.candidate_active_projects(request).data[:2]
        projects_list = []
        for data in candidate_active_projects:
            del data['project_details']
            projects_list.append(data)
        context = {
            'projects': {
            'results': projects_list,
            'total_results': active_projects['total_results']
            } if is_latest_version==1 else projects_list,
            'mylife_last_updated': candidate_query.mylife_last_updated,
            'profile_last_updated': candidate_query.profile_last_updated,
            'typical_day_last_updated': candidate_query.timeline_last_updated,
            'wakeup_time': candidate_query.wakeup_time,
            'timeline_completed': candidate_query.timeline_completed,
            'profile_percentage': get_profile_percentage(candidate_query),
            'modified': candidate_query.modified,
            'is_my_life_updated' : bool(request.user.lifestyle_responses),
            'is_typical_day_updated' : min_hours_filled_in_my_typical_day(request.user.id),
            'email' : request.user.email,
            'is_email_change' : bool(request.user.previous_email)
        }
        return Response(context)
    
    @staticmethod
    def update_mobile_app_version(request):
        """
            In Payload 'type' and 'version' is required.
            for IoS type is: 'ios'
            for Andriod type is: 'android'

            Based on this type we are updating the respective Column in Candidate table.
            Column for IoS app version: 'last_used_ios_app_version'
            Column for Andriod app version: 'last_used_andriod_app_version'
        """
        try:
            candidate_query = get_object_or_404(Candidate, id=request.user.id, active=True)
            device_type = request.data.get('type', None)
            app_version = request.data.get('version', None)
            
            # Check if any key value is None
            check_invalid([device_type, app_version])
            
            # Check the Given type is present in Defined Device types
            if device_type not in dict(DEVICE_TYPES):
                raise Exception
            
            # Update Versions Based on Device Types
            if device_type == 'ios':
                candidate_query.last_used_ios_app_version = app_version
            else:
                candidate_query.last_used_andriod_app_version = app_version
            candidate_query.save()
            context, status = {
                "message": updated
            }, 200
        except Exception:
            context, status = {
                "message": invalid_input
            }, 400
        return Response(context, status)


class TestAPI(ModelViewSet):

    def get(self, request):
        c = Candidate.objects.get(id=1)
        # get_relevant_exp(c)
        return Response(True)


class ReferralAPI(ModelViewSet):
    permission_classes = (AppUserAuthentication, AppVersionPermission,)

    @staticmethod
    def get_referral_text(request):
        return Response(message_response(referral_text(request.user)))


class CandidateSignUp(ModelViewSet):
    @staticmethod
    @swagger_auto_schema(request_body=SignupSerializer, operation_description='Signup_method: email_and_phone')
    def sign_up(request):
        hash_key = request.data.get('hash_key', None)
        email = str.lower(request.data.get('email')) if request.data.get('email') else None
        country_code = request.data.get('country_code', None)
        phone_number = request.data.get('phone', None)
        first_name = request.data.get('first_name', None)
        last_name = request.data.get('last_name', None)
        check_invalid([email, first_name, last_name, phone_number, country_code, hash_key])
        check_email(email)
        check_phone_number(phone_number)
        otp = generate_otp()
        request.data['otp'] = make_password(otp)
        serializer = CandidateSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                message = otp + ' is the OTP for verification at FlexiBees. Please use this to verify your phone number for FlexiBees. Do not share your OTP with anyone. ' + hash_key
                send_sms(serializer.data['country_code'], serializer.data['phone'], message) 
                candidate_obj = Candidate.objects.get(id=serializer.data['id'])
                candidate_obj.active = False
                candidate_obj.save()
                return Response({'user_id': candidate_obj.id, 'hash_key': hash_key})
            except Exception as e:
                log_data = [f"info|| {datetime.now()}: Exception occured in signUp api"]
                log_data.append(f"info|| {e}")
                api_logging(log_data)
                return Response(message_response(something_went_wrong), 400)
        return Response(serializer.errors, status=400)

    @staticmethod
    def verify_otp(request):
        user_id = request.data.get('user_id', None)
        mobile_otp = request.data.get('mobile_otp', None)
        email_otp = request.data.get('email_otp', None)
        check_invalid([user_id])
        user = None
        if email_otp:
            user = candidate_authenticate(user_id, email_otp)
            if user :
                user.email_verified = True
                user.save()
        if mobile_otp:
            user = candidate_verify_otp(user_id, mobile_otp)
            if user:
                user.phone_verified = True
                otp = generate_otp()
                user.password = make_password(otp)
                subject = 'Email Verification'
                template = 'otp_verification.html'
                recipients = [user.email]
                context = {
                    'username': user.first_name,
                    'otp': otp
                }
                email_send(subject, template, recipients, context)
                user.save()
        if not user:
            return Response(message_response(verification_failed), status=400)
        if user.phone_verified and user.email_verified and not user.active:
            try:
                Candidate.objects.filter(active=True, id=user_id).update(last_login=timezone.now())
                payload = jwt_payload_handler(user, 'candidate')
                WebUser.objects.filter(active=True, email=user.email).update(converted=True)
                WebUser.objects.filter(active=True, country_code=user.country_code, phone=user.phone).update(converted=True)
                user.active = True
                user.save()
                subject = 'Welcome to FlexiBees - Complete your Profile to access Flexible Work'
                template = 'signup.html'
                recipients = [user.email]
                context = {
                    'username': user.first_name
                }
                push_data = candidate_welcome(user.id)
                send_candidate_notification(users=[user.id], push_data=push_data)
                email_send(subject, template, recipients, context)
                if not user.timeline_completed and user.active and user.questionnaire_completed:
                    push_data = candidate_typical_day_notification(user.id)
                    send_candidate_notification(users=[user.id], push_data=push_data)
                context = {
                    'token': jwt_encode_handler(payload),
                    'user': CandidateDetailsSerializer(user).data
                }
                return Response(context)
            except Exception as e:
                log_data = [f"info|| {datetime.now()}: Exception occured in otp verification"]
                log_data.append(f"info|| {e}")
                api_logging(log_data)
                return Response(message_response(something_went_wrong), 400)
        return Response({'user_id': user.id})


class CandidateCityAPI(ModelViewSet):
    permission_classes = (AppUserAuthentication, AppVersionPermission,)

    @staticmethod
    def get_countries(request):
        try:
            search_term = request.GET.get('search_term', None)
            query = Q()
            if search_term:
                query &= Q(name__icontains=search_term)
            query &= Q(is_active=True)
            data = Country.objects.filter(query).order_by('name').values('id', 'name')
            return Response(data)
        except Exception as e:
            log_data = [f"info|| {datetime.now()}: Exception occured in countries listing api"]
            log_data.append(f"info|| {e}")
            api_logging(log_data)
            return Response(message_response(something_went_wrong), 400)  
    
    @staticmethod
    def get_cities(request, country):
        try:
            search_term = request.GET.get('search_term', None)
            query = Q()
            query &= Q(country=country)
            if search_term:
                query &= Q(name__icontains=search_term)
            query &= Q(is_active=True)
            data = City.objects.filter(query).order_by('name').values_list('name', flat=True)
            return Response(data)
        except Exception as e:
            log_data = [f"info|| {datetime.now()}: Exception occured in cities listing api"]
            log_data.append(f"info|| {e}")
            api_logging(log_data)
            return Response(message_response(something_went_wrong), 400) 

