import datetime
import threading
from apps import candidate
from apps.admin_app.views import api_logging
from apps.employer.serializers import EmployerSerializer, JobSerializer
from config.settings import EMPLOYER_SUPPORT_EMAILS, JOB_NOTIFIED_EMAILS
from core.emails import email_send
from core.helper_functions import api_exception_handler
from core.matching import calculate_matching_percentage, get_job_skills, get_work_experience_dict
from core.pagination import paginate, paginate_list   
from .helpers import check_duplicate, get_job_listing_query_filters,get_draft_query
from apps.common.helpers import send_email_verification, send_sms_verification, update_verifications, validate_email, validate_employer, validation_error_data
from apps.employer.models import CandidateJobStatus, Company, Employer, DraftJob, RolesMinMaxPricing, SkippedCandidate, Users
from apps.employer.models import Company, Employer, DraftJob, RolesMinMaxPricing, Users, InterviewSlot, Interview, SkippedCandidate
from apps.common.models import SkillMapping, UserType, RoleMapping
from django.db.models import Q, F
from apps.employer.permission_class import EmployerAuthentication
from apps.employer.constants import EMPLOYER, EMPLOYER_SUPPORT_SUBJECT, EMPLOYER_SUPPORT_TEMPLATE, INTERVIEW_CLEARED, INTERVIEW_REJECTED, INTERVIEW_SCHEDULED, JOB_CANDIDATE_INTERVIEW_SCHEDULED, JOB_CANDIDATE_REJECTED, JOB_SHORTLISTED, LOGIN, MOBILE_CHANGE, MOBILE_OTP_MESSAGE, DRAFT_JOB_PENDING, PROD, DRAFT_JOB_PUBLISHED, JOB_COMPLETED, \
    JOB_CREATED, PRICING_CONSTANT, SCHEDULED, TOTAL_NUMBER_OF_HOUR_IN_DAY, TOTAL_WORKING_DAYS_IN_WEEK, AVERAGE_WEEKS_IN_MONTH, DEFAULT_MONTHS, JOB_ID_NOT_MATCHED, \
    MAX_CANDIDATES, FEEDBACK_CLEARED, FEEDBACK_REJECTED, JOB_CANDIDATE_CLEARED, CANDIDATE_JOB_READY_STATE, CONTRACT_PENDING, CANDIDATE_JOB_STATUS_SCHEDULED, \
    CANDIDATE_JOB_STATUS_UPDATED, DEFAULT_JOB_DURATION, DEFAULT_CURRENCY, CANDIDATE_JOB_STATUS_IN_REVIEW, CUSTOM_STATUS_JOB_LIST, EXISTING_STATUS_JOB_LIST,\
    MAX_DRAFT_CANDIDATES, POSITION_FILLED_REJECTED, SLOT_BOOKING_EXCLUDE_THIS_DAYS, INTERVIEW_SLOTS_BOOKING_STATUS, EMPLOYER_JOB_STATUS_ACTIVE_STATE, TOTAL_SLOT_TO_BE_SELECTED, WITHIN_A_DAY, CANDIDATE_SELECTED_SUBJECT, CANDIDATE_SELECTED_TEMPLATE, ALLOWING_ONLY_SELECTED_AND_REJECTED, TIME_FORMAT_DEFINITION_FOR_JOB_DETAILS

from apps.employer.values import get_profile_values
from core.encryption import jwt_encode_handler, jwt_payload_handler
from core.extra import generate_otp, send_validation_error
from core.response_format import message_response
from apps.common.helpers import send_sms
from core.string_constants import CANDIDATE_RECOMMENDATION, DOMAIN_LIST, DRAFT_JOB_CREATE_UPDATE, DRAFT_JOB_DELETE, DRAFT_JOB_LIST, \
    DRAFT_JOB_RETRIVE, GET_PROFILE, JOB_CREATION, JOB_CREATION_FUNCTION, JOB_CREATION_ROLE, JOB_CREATION_SKILLS, JOB_DESCRIPTION_GENERATOR, JOB_DESC_GENERATOR_FAILED, JOB_DYNAMIC_QUESTION, \
    LINE_BREAK, DATE_FORMAT_STR, BLANK, LOGOUT, PROFILE_UPDATE, SIGNIN, SIGNUP, SUPPORT, VERIFY_OTP, DEACTIVATE, JOB_LISTING, JOBS_HOME_LISTING, MATCHING_CANDIDATES_LIST, PRICING_INTEGRATION_IN_JOB, INDIVIDUAL_JOB_DETAILS,\
     EMPLOYER_CANDIDATES_NOTES, EMPLOYER_CANDIDATES_NOTES_API, SHORTLIST_CANDIDATE, SKIP_CANDIDATE, EMPLOYER_TIME_SLOT_INTERVIEW,  SKIP_CANDIDATE, GET_SHORTLIST_CANDIDATES, UPDATE_FEEDBACK, INDIVIDUAL_JOB_DETAILS_STATUS, EMPLOYER_SLOT_DAYS_ERROR, EMPLOYER_SLOT_TIME_COLLISION, EMPLOYER_SLOT_TIME_FORMAT_ERROR, UNABLE_TO_FIND_FEEDBACK, VIEW_FEEDBACK_IDS, MAX_EMPLOYER_SLOT_TIME_PER_DAY, EMPLOYER_SLOT_EXISTING_COUNT

from core.validations import check_invalid
from flexibees_finance.settings import ENV
from apps.common.response_messages import user_not_found, invalid_otp, updated_successfully, validation_message_roleid, validation_message_function_id,\
    invalid_integer_field, logged_out_successfullly, mobile_arleady_exists, something_went_wrong, validation_skill_list_error,job_creartion_check_draft_id, \
    validation_message_roleid, draft_job_already_created, deactivated_successfullly, deleted_successfully, created_successfully
from core.response_messages import invalid_input
from apps.common.response_messages import status_message_success, status_message_failure
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from apps.employer.models import  JobCustomRoleSkills,  DraftJob ,Employer, Job, CandidateJobNotes, CandidateJobStatus
from apps.common.models import  SkillMapping ,CustomSkill, CustomRole
from apps.admin_app.models import  Domain, Role, Skill, Function
from django.db.models import Q, Count
from apps.admin_app.models import Domain 
from apps.candidate.models import Candidate, ClientFeedback, Education
from django.db import transaction
from apps.common.constants import PENDING_STATUS,  REJECTED_STATUS
from scripts.openai_scripts import AIServiceWrapperIntegration
import os
import json
from pathlib import Path
from apps.employer.models import RolesMinMaxPricing
from crons.candidate_pricing_algo import CandidatePricingAlgorithm
from core.model_choices import (EMPLOYER_COMPANY_SIZE, EMPLOYER_SOURCE,EMPLOYER_STATUS, EMPLOYER_JOB_STATUS, EMPLOYER_TARGET_AUDIENCE, JOB_DRAFT_STATUS, CANDIDATE_STATES, PROJECT_STATES, CLIENT_STATES, FEEDBACK_STATUS, CANDIDATE_JOB_STATUS)
from apps.common.constants import APPROVAL_STATUS
from django.contrib.postgres.aggregates import ArrayAgg
from datetime import  timedelta
from .messages import notification_sent

# Create your views here.


class EmployerSignUpLoginViewset(ModelViewSet):

    @staticmethod
    @api_exception_handler(SIGNUP)
    def signUp(request):
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        check_invalid([first_name, last_name, email])
        validate_email(email)
        user_type = UserType.objects.filter(type_name=EMPLOYER).first()
        if not user_type:
            return Response(message_response(something_went_wrong), status=status.HTTP_404_NOT_FOUND)
        otp = generate_otp()
        user = Users.objects.create(email=email, is_active=False, first_name=first_name, last_name=last_name, otp=make_password(otp), type=user_type)
        employer = Employer.objects.create(user=user, is_active=False)
        subject='Email Verification'
        template='otp_verification.html'
        send_email_verification(user.email, user.first_name, otp, template, subject)
        return Response({'id': employer.id, 'email': employer.user.email}, status=status.HTTP_200_OK)

    @staticmethod
    @api_exception_handler(VERIFY_OTP)
    def verify_otp(request):
        data = request.data
        request_type = data.get('request_type')
        email = data.get('email')
        query = Q(id=data.get('id'))
        if request_type in [LOGIN, MOBILE_CHANGE]:
            query &= Q(is_active=True)
        else:
            check_invalid([email])
            validate_email(email)
            query &= Q(is_active=False)
        employer = Employer.objects.filter(query).first()
        if not employer:
            return Response(message_response(user_not_found), status=status.HTTP_404_NOT_FOUND)
        validate_employer(employer, request_type)
        otp = data.get('otp')
        # Verify the provided OTP against the hashed OTP stored in the database.
        try:
            if ENV!= PROD or employer.user.check_otp(otp):
                if request_type == MOBILE_CHANGE:
                    employer.user.mobile = employer.additional_info.get("mobile")
                    employer.user.country_code = employer.additional_info.get("country_code")
                    employer.user.phone_verified = True
                    employer.user.otp = None
                    employer.additional_info.pop("mobile")
                    employer.additional_info.pop("country_code")
                    employer.user.save()
                    employer.save()
                    return Response(message_response(updated_successfully), status=status.HTTP_200_OK)
                update_verifications(employer, request_type)
                employer.user.otp = None
                employer.user.email_verified = True
                employer.user.save()
                employer.user.is_active = True
                employer.is_active = True
                employer.user.password = make_password(otp)
                employer.user.save()
                employer.save()
                # Generate and return a token for the employer if both verifications are complete.
                payload = jwt_payload_handler(employer.user, EMPLOYER)
                context = {
                    'token': jwt_encode_handler(payload),
                    'user':{
                        "first_name": employer.user.first_name,
                        "last_name": employer.user.first_name,
                        "email": employer.user.email
                    }
                }
                return Response(context, status=status.HTTP_200_OK)
            else:
                # If the OTP is incorrect, return a 400 error response.
                return Response(message_response(invalid_otp), status=status.HTTP_400_BAD_REQUEST)
        except Exception:
                return Response(message_response(invalid_otp), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    @api_exception_handler(SIGNIN)
    def login(request):
        user_obj = None
        if 'email' in request.data:
            email = request.data.get('email')
            check_invalid([email])
            # check if active user with email
            user_obj = Employer.objects.filter(user__email__iexact=email, is_active=True).first()
        else:
            country_code = request.data.get('country_code')
            mobile = request.data.get('mobile')
            check_invalid([country_code, mobile])
            # check if active user with phone
            user_obj = Employer.objects.filter(user__mobile__iexact=mobile,
                                        user__country_code__iexact=country_code, is_active=True).first()
        if not user_obj:
            return Response(message_response(user_not_found), status=status.HTTP_400_BAD_REQUEST) 
        otp = generate_otp()
        print("employer otp ",otp)
        # send email or sms
        if 'email' in request.data:
            subject = 'Email Verification'
            template = 'otp_verification.html'
            send_email_verification(user_obj.user.email, user_obj.user.first_name, otp, template, subject)
        else:
            send_sms_verification(user_obj.user.country_code, user_obj.user.mobile, otp)
        user_obj.user.otp = make_password(otp)
        user_obj.user.save()
        return Response({'user_id': user_obj.id})



class DraftJobViewset(ModelViewSet):
    permission_classes = [EmployerAuthentication]

    @staticmethod
    @api_exception_handler(DRAFT_JOB_CREATE_UPDATE)
    def update(request):
        data = request.data
        if 'id' in data:
            query = Q(id=data.get('id'))
            query &= Q(status=DRAFT_JOB_PENDING)
            query &= Q(employer=request.user)
            query &= Q(is_active=True)
            draft_job = DraftJob.objects.filter(query).first()
            if not draft_job:
                return Response(message_response(invalid_input), status=status.HTTP_400_BAD_REQUEST)
            DraftJob.objects.filter(query).update(details=data)
        else:
            draft_job = DraftJob.objects.create(details=data, employer=request.user)
        return Response({'id': draft_job.id}, status=status.HTTP_200_OK)
        
    @staticmethod
    @api_exception_handler(DRAFT_JOB_RETRIVE)
    def retrive(request, id):
        draft_job = DraftJob.objects.filter(id=id, status=DRAFT_JOB_PENDING, employer=request.user, is_active=True).values('id', 'details').first()
        if not draft_job:
            return Response(message_response(invalid_input), status=status.HTTP_400_BAD_REQUEST)
        return Response(draft_job, status=status.HTTP_200_OK)
    
    @staticmethod
    @api_exception_handler(DRAFT_JOB_DELETE)
    def delete(request, id):
        draft_job = DraftJob.objects.filter(id=id, status=DRAFT_JOB_PENDING, employer=request.user, is_active=True).first()
        if not draft_job:
            return Response(message_response(invalid_input), status=status.HTTP_400_BAD_REQUEST)
        draft_job.is_active = False
        draft_job.save()
        return Response(message_response(deleted_successfully), status=status.HTTP_200_OK)
    
    @staticmethod
    @api_exception_handler(DRAFT_JOB_LIST)
    def list(request):
        log_data = [f"info|| {datetime.datetime.now()}: draft jobs list API"]
        page = request.data.get('page_no', 1)
        page_size = request.data.get('page_size', 10)
        filters = request.data.get('filters', {})
        try:
            query = get_draft_query(filters, request.user)
            draft_jobs = list(DraftJob.objects.filter(query).values('id', 'details', 'updated_at').order_by('-id')[(page - 1) * page_size:page * page_size])
            role_ids = [job_obj['details']['existing_role'].get('role_id') for job_obj in draft_jobs if job_obj['details'].get('existing_role') and job_obj['details']['existing_role'].get('role_id')]
            # get pricing from model
            role_pricing = RolesMinMaxPricing.objects.filter(existing_role__id__in=role_ids)
            map_role_pricing = {}
            # convert pricing to dictionary 
            for pricing in role_pricing:
                if pricing.existing_role and pricing.existing_role.id not in map_role_pricing:
                    map_role_pricing[pricing.existing_role.id]=pricing
            # update the pricing details 
            for job_obj in draft_jobs:
                if job_obj['details'].get('existing_role') and job_obj['details']['existing_role'].get('role_id') and map_role_pricing.get(job_obj['details']['existing_role']['role_id']):
                    job_obj['price'] = (map_role_pricing[job_obj['details']['existing_role']['role_id']].min_salary + map_role_pricing[job_obj['details']['existing_role']['role_id']].max_salary) // 2
                else:
                    job_obj['price'] = None
            count = DraftJob.objects.filter(query).count()
            return Response(paginate_list(draft_jobs, count, page, page_size))
        except Exception as e:
            
            error_message = validation_error_data(e)
            context = {
                "request_url": request.META['PATH_INFO'], "error": e, "payload": request.data}
            log_data.append(f"info || context :{context}")
            log_data.append(LINE_BREAK)
            api_logging(log_data)
            return Response(message_response(error_message), status=status.HTTP_400_BAD_REQUEST)


class JobViewSet(ModelViewSet):
    # permission_classes = [EmployerAuthentication]

    @staticmethod
    @api_exception_handler(JOB_LISTING)
    def list(request):
        """
        Job listing api
        """
        filters = request.data.get('filters', {})
        page = request.data.get('page_no', 1)
        page_size = request.data.get('page_size', 10)
        is_all_jobs = request.data.get('is_all_jobs')
        sort = request.data.get('sort')
        query, draft_query, values, other_values, sort = get_job_listing_query_filters(filters, sort, is_all_jobs, request.user)
        query &= Q(employer=request.user)
        job_objs = list(Job.objects.filter(query).values(*values).annotate(**other_values).distinct().order_by(sort)[(page - 1) * page_size:page * page_size])
        role_ids = [job_obj['role_id'] for job_obj in job_objs if job_obj.get('role_id')]
        custom_role_ids = [job_obj['custom_role_id'] for job_obj in job_objs if job_obj.get('custom_role_id')]
        # get pricing from model
        role_pricing = RolesMinMaxPricing.objects.filter(Q(Q(existing_role__id__in=role_ids) | Q(custom_role__id__in=custom_role_ids)))
        map_role_pricing = {}
        map_custom_role_pricing = {}
        # convert pricing to dictionary 
        for pricing in role_pricing:
            if pricing.existing_role and pricing.existing_role not in map_role_pricing:
                map_role_pricing[pricing.existing_role.id]=pricing
            elif pricing.custom_role and pricing.custom_role not in map_custom_role_pricing:
                map_custom_role_pricing[pricing.custom_role.id]=pricing
        # update the pricing details 
        for job_obj in job_objs:
            # update role price 
            if job_obj.get('role_id') and map_role_pricing.get(job_obj['role_id']):
                job_obj['price'] = (map_role_pricing[job_obj['role_id']].min_salary + map_role_pricing[job_obj['role_id']].max_salary) // 2
                job_obj['currency'] = DEFAULT_CURRENCY
            # update custom role price 
            elif job_obj.get('custom_role_id') and map_custom_role_pricing.get(job_obj['custom_role_id']):
                job_obj['price'] = (map_custom_role_pricing[job_obj['custom_role_id']].min_salary + map_custom_role_pricing[job_obj['custom_role_id']].max_salary) // 2
                job_obj['currency'] = DEFAULT_CURRENCY
            else:
                job_obj['price'] = None
            job_obj.pop('role_id')
            job_obj.pop('custom_role_id')
        count = Job.objects.filter(query).count()
        # update the draft jobs 
        if is_all_jobs:
            job_objs += list(DraftJob.objects.filter(draft_query).values('id', 'details', 'updated_at')[(page - 1) * page_size:page * page_size])
            count += DraftJob.objects.filter(draft_query).count()
            # sort the results based on recently updated and paginate
            job_objs = sorted(job_objs, key=lambda x: x['updated_at'], reverse=True)[(page - 1) * page_size:page * page_size]
        return Response(paginate_list(job_objs, count, page, page_size))
    
    @api_exception_handler(JOBS_HOME_LISTING, is_staticmethod=False)
    def home(self, request):
        """
        This method prepares and returns a response containing job-related data filtered by different statuses.
        The data includes draft jobs, created jobs, interview scheduled jobs, and contract completed jobs.
        
        Parameters:
        - request: The HTTP request object.

        Returns:
        - Response: A dictionary containing lists of jobs categorized by their respective statuses.
        """
        payload = {'page_no': 1, 'page_size':3}
        request.data.update(payload)
        # draft jobs 
        draft_jobs = DraftJobViewset.list(request).data['results']
        # created jobs 
        request.data.update({'filters': {'status': JOB_CREATED}})
        created_jobs = self.list(request).data['results']
        # interview scheduled jobs 
        request.data.update({'filters': {'status': JOB_CANDIDATE_INTERVIEW_SCHEDULED}})
        feedback_jobs = self.list(request).data['results']
        # contract completed jobs 
        request.data.update({'filters': {'status': CONTRACT_PENDING}})
        contract_completed = self.list(request).data['results']
        context ={
            'draft_jobs': draft_jobs,
            'created_jobs': created_jobs,
            'feedback_jobs': feedback_jobs,
            'contract_completed': contract_completed,
        }
        return Response(context)

class IndividualJobDeatils(ModelViewSet):

    @staticmethod
    @api_exception_handler(INDIVIDUAL_JOB_DETAILS_STATUS)
    def get_list_of_status(job_objects):
        """
        Retrieves a list of candidate job statuses for a given job.

        This method generates a list of statuses associated with a job object, including status name, 
        status ID, and a formatted timestamp. The initial status is always included, and additional 
        statuses are appended based on specific conditions.

        Args:
            job_objects (Job): The job object for which the candidate job statuses are retrieved.

        Returns:
            tuple: A tuple containing:
                - bool: Indicates success (True) or failure (False).
                - list or Exception: On success, a list of dictionaries with status details. 
                    On failure, the exception encountered.
        """
        try:
            candidate_job_status = [{
                "status_name":CANDIDATE_JOB_STATUS[1][1],
                "status_id":CANDIDATE_JOB_STATUS[1][0],
                "status_timestamp":str(job_objects.created_at.strftime(TIME_FORMAT_DEFINITION_FOR_JOB_DETAILS))
            }]

            for  status in CANDIDATE_JOB_STATUS:
                if status[0] != CANDIDATE_JOB_STATUS_IN_REVIEW:
                    candidate_job_status_obj = CandidateJobStatus.objects.filter(job = job_objects,status = status[0]).order_by('id')
                    if candidate_job_status_obj.exists():
                        candidate_job_status_obj = candidate_job_status_obj.first()
                        # If the object is exist it means Interview has scheduled for candidate 
                        candidate_job_status.append({
                            "status_name": CANDIDATE_JOB_STATUS[0][1],
                            "status_id":CANDIDATE_JOB_STATUS[0][0],
                            "status_timestamp":str(candidate_job_status_obj.created_at.strftime(TIME_FORMAT_DEFINITION_FOR_JOB_DETAILS))
                        })
                        if status[0] in ALLOWING_ONLY_SELECTED_AND_REJECTED:
                            candidate_job_status.append({
                            "status_name": status[1],
                            "status_id": status[0],
                            "status_timestamp":str(candidate_job_status_obj.updated_at.strftime(TIME_FORMAT_DEFINITION_FOR_JOB_DETAILS))
                        })

            return True, candidate_job_status
        except Exception as e:
            return False,e

    @staticmethod
    @api_exception_handler(INDIVIDUAL_JOB_DETAILS)
    def job_details(request):
        """
        Retrieve detailed information about a specific job.

        This method handles a GET request to fetch the details of a job based on the provided job_id.
        It constructs a response containing job status, skills list, job description, role name, and company details.

        Args:
            request (Request): The HTTP request object containing the job_id as a GET parameter.

        Returns:
            Response: A Response object containing the job details
        """
        try:
            res_format = {
                "status":400,
                "status_messages":"Invalid Input",
            }
            job_id = request.GET.get("job_id")
            job_objects = Job.objects.filter(pk= job_id)
            if job_objects.exists() == False:
                res_format['errors'] = JOB_ID_NOT_MATCHED
                return Response(res_format, 400)
            job_objects =  job_objects.first()

            role_name = ""
            employer = job_objects.employer
            company = employer.company
            skills_list =  list(job_objects.skills.all().values_list("tag_name",flat = True))

            custom_models = JobCustomRoleSkills.objects.filter(job = job_objects)

            existing_role = job_objects.role
            pricing_job = 0
            query = Q()
            if existing_role :
                role_name = existing_role.tag_name
                query = Q(existing_role = existing_role )
                

            if custom_models.exists():
                custom_models = custom_models.first()
                skills = list(custom_models.skill.exclude(status = APPROVAL_STATUS ).values_list("skill_name",flat = True))
                skills_list = skills_list + skills
                if role_name == "":
                    custom_role =custom_models.role
                    if custom_role:
                        role_name = custom_role.role_name
                        query = Q(custom_role = custom_role )
            pricing_obj = RolesMinMaxPricing.objects.filter(query).order_by("-id").first()
            pricing_job = round((pricing_obj.min_salary + pricing_obj.max_salary)// PRICING_CONSTANT) if pricing_obj else ""

            details = job_objects.details
            experience = details.get("experience","")
            job_type = details.get("job_type","")
            location = details.get("location","")
            job_duration = f"{str(details.get('job_duration',DEFAULT_MONTHS))}"
            if "months" not in job_duration :
                job_duration = job_duration + " months"
            
            # This function fetch all list of candidate status as per job based .
            job_status_as_per_candidates = IndividualJobDeatils.get_list_of_status(job_objects)[1]

            job_details = {
                "pricing_job" : pricing_job,
                "pricing_currency": DEFAULT_CURRENCY,
                "job_function_name": job_objects.function.tag_name,
                "experience":experience,
                "job_type": job_type,
                "location": location,
                "job_status": job_status_as_per_candidates,
                "skills_list": skills_list,
                "job_duration":job_duration,
                "job_description": job_objects.description if job_objects.description else "",
                "role_name":role_name,
                "company_details":{
                    "company_name":company.name,
                    "website": company.website,
                    "industry_type": company.industry_type.tag_name,
                    "size": EMPLOYER_COMPANY_SIZE[(int(company.size)-1)][-1] if company.size else "",
                    "target_audience": EMPLOYER_TARGET_AUDIENCE[(int(company.target_audience)-1)][-1] if company.target_audience else "" ,
                    "source": EMPLOYER_SOURCE[(int(company.source)-1)][-1] if company.source else ""
                },
                "created_at" : str(job_objects.created_at.date())
            }
            res_format['data'] = job_details
            res_format['status'] = 200
            res_format['status_messages'] = 'Success'
            return Response(res_format,200)
        except Exception as e:
            log_data = [f"error|| {datetime.datetime.now()}: {e}"]
            api_logging(log_data)
            res_format = {
                "status":400,
                "status_messages":"Invalid Input",
                "errors": str(e)
            }
            return Response(res_format,400)    


class JobCandidate(ModelViewSet):
    permission_classes = [EmployerAuthentication]

    @staticmethod
    @api_exception_handler(SKIP_CANDIDATE)
    def skip(request):
        job = request.data.get('job')
        candidate = request.data.get('candidate')
        check_invalid([job, candidate])
        if check_duplicate(candidate, job, request.user):
            return Response(message_response(invalid_input), status=status.HTTP_400_BAD_REQUEST)
        SkippedCandidate.objects.create(job_id=job, candidate_id=candidate)
        return Response(message_response(updated_successfully), status=status.HTTP_200_OK)

    permission_classes = [EmployerAuthentication]

    @staticmethod
    @api_exception_handler(SUPPORT)
    def employer_support(request):
        message = request.data.get('message')
        if not message:
            return Response(message_response(invalid_input), status=status.HTTP_400_BAD_REQUEST)
        subject = EMPLOYER_SUPPORT_SUBJECT
        template = EMPLOYER_SUPPORT_TEMPLATE
        recipients = EMPLOYER_SUPPORT_EMAILS
        context = {
            'username': request.user.user.first_name,
            'message': message,
            'email': request.user.user.email or None,
            'country_code': request.user.user.country_code,
            'phone': request.user.user.mobile or None,
        }

        email_send(subject, template, recipients, context)
        return Response(message_response(notification_sent), status=status.HTTP_200_OK)
    
    
class EmployerViewSet(ModelViewSet):
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer
    
    
class JobListViewSet(ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer