import datetime
import logging
from time import sleep

from django.shortcuts import get_object_or_404

from apps.admin_app.models import Role, Skill
from apps.admin_app.serializers import AdminLoginSerializer, AdminUserDetailSerializer, RoleSerializer, SkillListingSerializer, SkillSerializer
from core.api_permissions import AdminAuthentication
from core.encryption import jwt_encode_handler, jwt_payload_handler
from core.response_format import message_response

from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from core.response_messages import login_failed, deleted, created, updated, tag_exist
from core.validations import check_invalid

from core.authentication import admin_authenticate

from django.utils import timezone


def api_logging(log_data):
    """
    Function used to log all the API requests and responses along with error if any.
    Creates log files on daily basis.
    Params:
    1. log_data: list of individual logs having log type and message.
    """
    # Create Log file in logs folder:
    log_dir = 'logs'
    logging.basicConfig(
        filename=f"{log_dir}/api_requests_{datetime.datetime.now().date()}.log", level=logging.DEBUG)
    try:
        for log in log_data:
            message = log.split("||")
            if message[0] == 'info':
                logging.info(message[1])
            else:
                logging.error(message[1])
    except Exception as e:
        logging.error(f"Log function error: {str(e)}")
    logging.info("=" * 150)
    return True


class TimeoutAPI(ModelViewSet):

    def timeout(self, request, time):
        sleep(time)
        return Response(message_response('Response after ' + str(time)))
    

class AdminLoginAPI(ModelViewSet):
    serializer_class = AdminLoginSerializer

    @staticmethod
    def login(request):
        email = request.data.get('email')
        password = request.data.get('password')
        role = request.data.get('admin_role')
        print("email ",email)
        print("password ",password)
        print("role ",role)
        check_invalid([email, password, role])
        user = admin_authenticate(email, password, role)
        if user:
            payload = jwt_payload_handler(user, role)
            user.last_login = timezone.now()
            user.active = True
            user.save()
            context = {
                'token': jwt_encode_handler(payload),
                'user': AdminUserDetailSerializer(user).data
            }
            return Response(context)
        return Response(message_response(login_failed), status=400)

