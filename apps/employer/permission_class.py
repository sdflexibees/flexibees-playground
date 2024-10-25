from apps.employer.models import Employer
from rest_framework.permissions import BasePermission
from core.encryption import (jwt_decode_handler, crypto_decode)


class EmployerAuthentication(BasePermission):
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
            request.user = Employer.objects.get(user__id=int(user_id), user__password=pwd, is_active=True)
            request.role = 'Employer'
            return True
        except Exception:
            return False