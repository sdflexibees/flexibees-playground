from django.core.exceptions import ObjectDoesNotExist

from apps.admin_app.models import AdminUser

# from user_app.models import AppUser
from apps.candidate.models import Candidate
from core.extra import generate_otp


def user_authenticate(username, password):

    """
    Authenticate the user based on user type
    1. on the basis of email + password
    :param username: required
    :param password: required
    :return: if success AppUser object, otherwise pass
    """
    try:
        user = AppUser.objects.get(username__iexact=username, active=True)
        if user.check_password(password):
            return user
    except ObjectDoesNotExist:
        return None


def candidate_authenticate(user_id, password):
    try:
        user = Candidate.objects.get(id=user_id)
        if user.check_password(password):
            # if password == '1234':
            #     user.password = password
            #     user.save()
            # else:
            user.set_password(generate_otp())
            user.save()
            return user
    except ObjectDoesNotExist:
        return None
    
def candidate_verify_otp(user_id, password):
    try:
        user = Candidate.objects.get(id=user_id)
        if user.check_otp(password):
            return user
    except ObjectDoesNotExist:
        return None
