from collections import defaultdict
import datetime
from apps.admin_app.views import api_logging
from config.settings import IMAGE_MAX_SIZE
from core.constants import EMPLOYER_ALLOWED_ATTACHMENT_EXTENSIONS, EMPLOYER_ALLOWED_IMAGE_EXTENSIONS, IMAGE_DIRECTORY
from core.file_upload import upload_to_s3_bucket
from core.helper_functions import api_exception_handler
from core.validations import check_invalid
from .helpers import validation_error_data
from apps.common.models import SkillMapping, RoleMapping
from core.extra import send_validation_error
from core.response_format import message_response
from core.string_constants import ASSET_UPLOAD, CUSTOM_ROLE_APPROVAL, LINE_BREAK, DATE_FORMAT_STR, ROLE_LISTING_VIEWER, ROLE_SKILLS_LISTING, UPDATE_ROLE_NAME, UPDATE_SKILL_NAME
from .constants import PENDING_STATUS, APPROVAL_STATUS, REJECTED_STATUS, ROLE_MAPPING_PRIORITY
from flexibees_candidate.settings import ENV
from .response_messages import custum_approval_role_already_approved, status_message_failure, \
    status_message_success, custum_already_rejected, custum_approval_role_already_approved,\
    custum_role_already_approved, custum_role_rejected, custum_role_already_existing_mapping_table, custum_role_approved, \
    custum_skill_rejected, custum_skill_already_existing_mapping_table, custum_skill_approved, custum_skill_is_already_approved, \
    custum_skill_not_found, custum_role_not_approved, page_size_message, page_number_message, \
    validation_message_roleid, validation_message_role_name, validation_message_role_status, validation_message_function_id, \
    validation_message_function_name, role_mapping_object_not_found, role_exists, custom_role_exists, updated_successfully, \
    skill_exists, custom_skill_exists, invalid_input
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from .models import CustomRole, SkillMapping ,CustomSkill
from apps.employer.models import Job, JobCustomRoleSkills, RolesMinMaxPricing
from core.model_choices import CUSTUM_ROLES_SKILLS_STATUS
from apps.admin_app.models import Role, Skill
from django.utils import timezone
from django.db import transaction
from django.db.models import F
from core.api_permissions import AdminAuthentication


# Create your views here.
class AssetUpload(ModelViewSet):
    
    """
    AssetUpload - upload the images
    """
    @staticmethod
    @api_exception_handler(ASSET_UPLOAD)
    def post(request):
        try:
            upload_file = request.data['file']
            # spliting the extension
            file_extension = upload_file.name.split('.')[-1]
            # allowed extensions 
            allowed_extensions = EMPLOYER_ALLOWED_IMAGE_EXTENSIONS + EMPLOYER_ALLOWED_ATTACHMENT_EXTENSIONS
            if file_extension not in allowed_extensions:
                return Response(message_response(invalid_input), status=400)
        except Exception:
            return Response(message_response(invalid_input), status=400)

        check_invalid([upload_file])

        # Fetch the file size
        file_size = len(upload_file)
        
        # validating the size of the file
        if file_size > int(IMAGE_MAX_SIZE):
            return Response(message_response(invalid_input), status=400)

        # upload the Image
        url = upload_to_s3_bucket(request.data['file'], IMAGE_DIRECTORY, file_extension)
        return Response({'url': url})
