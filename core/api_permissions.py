from rest_framework.permissions import BasePermission
from apps.admin_app.models import AdminUser
from apps.candidate.models import Candidate
from .encryption import (jwt_decode_handler, crypto_decode)
from rest_framework.exceptions import APIException
from core.response_format import message_response
from flexibees_finance.settings import APP_VERSION
from core.response_messages import update_app

# from user_app.models import AppUser


class AppUserAuthentication(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        try:
            user_id = crypto_decode(
                    jwt_decode_handler(
                        request.META['HTTP_AUTHORIZATION']
                    )['ai']
            )
            pwd = crypto_decode(
                    jwt_decode_handler(
                        request.META['HTTP_AUTHORIZATION']
                    )['bi']
            ) if jwt_decode_handler(
                        request.META['HTTP_AUTHORIZATION']
                    )['bi'] != '' else ''
            request.user = Candidate.objects.get(id=int(user_id), password=pwd, active=True)
            request.role = 'Candidate'
            return True
        except:
            return False


class AdminAuthentication(BasePermission):
    """
    Allows access only to authenticated admins.
    """

    def has_permission(self, request, view):
        try:
            user_id = crypto_decode(
                    jwt_decode_handler(
                        request.META['HTTP_AUTHORIZATION']
                    )['ai']
            )
            pwd = crypto_decode(
                    jwt_decode_handler(
                        request.META['HTTP_AUTHORIZATION']
                    )['bi']
            ) if jwt_decode_handler(
                        request.META['HTTP_AUTHORIZATION']
                    )['bi'] != '' else ''
            role = jwt_decode_handler(request.META['HTTP_AUTHORIZATION']).get('ci', '')
            request.user = AdminUser.objects.get(id=int(user_id), password=pwd, active=True, published=True,
                                                    roles__contains=[role])
            request.role = role
            return True
        except:
            return False

class AppVersionException(APIException):
    status_code = 400
    default_detail = {'message': update_app}


class AppVersionPermission(BasePermission):
    def has_permission(self, request, view):
        try:
            version = request.META.get('HTTP_VERSION',None)
            if not version or version not in APP_VERSION:
                raise AppVersionException
            return True
        except Exception:
            raise AppVersionException