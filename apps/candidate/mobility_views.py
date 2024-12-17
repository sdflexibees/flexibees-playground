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
from flexibees_finance.settings import APPTEST_USERID

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
from flexibees_finance.settings import SUPER_ADMIN_ROLE, SUPER_ADMIN_EMAIL, ITEM_TYPE_CANDIDATE, SENT_TO_TYPE_SUPER_ADMIN, SENT_TO_TYPE_RECRUITER, SENT_TO_TYPE_RECRUITER_ADMIN
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
        print("otp ",otp)
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
        print("otp ",otp)
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

