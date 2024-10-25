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
    

class SkillAPI(ModelViewSet):
    # permission_classes = (AdminAuthentication,)
    serializer_class = SkillSerializer
    detail_serializer_class = SkillListingSerializer

    def create(self,request, pk=None):
        """
        Create skill
        :param request: tag_name, function
        :return: id, tag_name, function
        """
        new_tags = request.data.get("name")
        for tag in new_tags:
            request.data['name'] = tag
            existing_tag = Skill.objects.filter(tag_name__iexact=tag)
            if len(existing_tag) > 0:
                if existing_tag[0].active:
                    return Response(message_response(tag_exist), 400)
                existing_tag[0].active = True
                existing_tag[0].save()
            else:
                serializer = SkillSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                with open("skills.csv", 'a') as f:
                    f.write(',' + tag.title() + ',' + tag.lower())

        return Response(message_response(created))

    def retrieve(self, request, pk):
        """
        Skill detail
        :param request: id
        :return: id, tag_name, function
        """
        skill_obj = get_object_or_404(Skill, active=True, id=pk)
        serializer = SkillListingSerializer(skill_obj).data
        return Response(serializer)

    def list(self, request):
        """
        Skill listing
        :param request: id
        :return: id, tag_name, function
        """
        skill_objs = Skill.objects.filter(active=True).order_by('-id')
        serializer = SkillListingSerializer(skill_objs, many=True)
        return Response(serializer.data)

    def partial_update(self, request, pk):
        """
        Skill edit
        :param request: id
        :return: id, tag_name, function
        """
        skill_obj = get_object_or_404(Skill, id=pk, active=True)
        serializer = SkillSerializer(skill_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(message_response(updated), 200)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk):
        """
        Delete skill
        :param request: id
        :return: message
        """
        skill_obj = get_object_or_404(Skill, id=pk, active=True)
        skill_obj.active = False
        skill_obj.save()
        return Response(message_response(deleted), 200)


class RoleAPI(ModelViewSet):
    # permission_classes = (AdminAuthentication,)
    serializer_class = RoleSerializer

    def create(self,request, pk=None):
        """
        Create role
        :param request: tag_name
        :return: id, tag_name
        """
        new_tags = request.data.get("name")
        for tag in new_tags:
            request.data['name'] = tag
            existing_tag = Role.objects.filter(tag_name__iexact=tag)
            if len(existing_tag) > 0:
                if existing_tag[0].active:
                    return Response(message_response(tag_exist), 400)
                existing_tag[0].active = True
                existing_tag[0].save()
            else:
                serializer = RoleSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
        return Response(message_response(created))

    def retrieve(self, request, pk):
        """
        Role detail
        :param request: id
        :return: id, tag_name
        """
        role_obj = get_object_or_404(Role, active=True, id=pk)
        serializer = RoleSerializer(role_obj).data
        return Response(serializer)

    def list(self, request):
        """
        Role listing
        :param request: id
        :return: id, tag_name
        """
        role_objs = Role.objects.filter(active=True).order_by('-id')
        serializer = RoleSerializer(role_objs, many=True)
        return Response(serializer.data)

    def partial_update(self, request, pk):
        """
        Role edit
        :param request: id
        :return: id, tag_name
        """
        role_obj = get_object_or_404(Role, id=pk, active=True)
        serializer = RoleSerializer(role_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk):
        """
        Delete role
        :param request: id
        :return: message
        """
        role_obj = get_object_or_404(Role, id=pk, active=True)
        role_obj.active = False
        role_obj.save()
        return Response(message_response(deleted), 200)



