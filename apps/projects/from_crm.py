import datetime, logging, os

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from apps.admin_app.models import AdminUser, Function, Role, Configuration
from apps.admin_app.serializers import SearchListSerializer
from apps.notifications.views import notify_admin
from apps.projects.models import Project
from apps.projects.serializers import CRMListSerializer, CRMSerializer
from core.api_permissions import AdminAuthentication
from core.pagination import paginate
from core.response_format import message_response
from core.response_messages import update_proj_detail, updated, role_model_validate, something_went_wrong
from core.zoho import get_crm_data
from apps.admin_app.views import api_logging
from flexibees_finance.settings import MAX_CHARS_ID, MAX_CHARS_DEAL_NAME, MAX_CHARS_ACCOUNT_NAME, MAX_CHARS_CONTACT_NAME, MAX_CHARS_ROLE_TYPE, MAX_CHARS_MODEL_TYPE, MAX_CHARS_FLEXI_DETAILS, MAX_CHARS_STAGE, FIRST_STAGE_STATUS


def has_crm_project_in_db(existing_records, zoho_id):
    for record in existing_records:
        if record['zoho_id']==str(zoho_id):
            return record
    return {}

def check_change(project_query, each_data, role_type, model_type,role_obj):
    return project_query['deal_name'] == each_data['Deal_Name'] and project_query['company_name']== each_data['Account_Name']['name'] and project_query['contact_name'] == each_data['Contact_Name']['name'] and project_query['role_type'].lower()== role_type.lower() and project_query['model_type'].lower() == model_type.lower() and project_query['flex_details'] == str(each_data.get('Pricing_Expectation_was_Lower_than_Ours', '') or '') and project_query['stage'] == str(each_data.get('Stage', '') or '') and project_query['next_step'] == str(each_data.get('Next_Steps', '') or '') and project_query['status_description'] == str(each_data.get('Description', '') or '') and project_query['role_id'] == role_obj

def check_length(data,role_type,model_type,api_logging): 
    if len(data['id']) <= MAX_CHARS_ID and len(data['Deal_Name']) <= MAX_CHARS_DEAL_NAME and len(data['Account_Name']['name']) <= MAX_CHARS_ACCOUNT_NAME and len(data['Contact_Name']['name']) <= MAX_CHARS_CONTACT_NAME and len(role_type) <= MAX_CHARS_ROLE_TYPE and len( model_type) <= MAX_CHARS_MODEL_TYPE and len(str(data.get('Pricing_Expectation_was_Lower_than_Ours', '') or '')) <= MAX_CHARS_FLEXI_DETAILS and len(str(data.get('Stage', '') or '')) <= MAX_CHARS_STAGE :
        return True
    api_logging([f"info|| {datetime.datetime.now()}: pull_from_crm","error||length of the charecters is greater tham max length",f"info||{data}"])
    return False
