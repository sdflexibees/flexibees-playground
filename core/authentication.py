from django.core.exceptions import ObjectDoesNotExist

from apps.admin_app.models import AdminUser

# from user_app.models import AppUser
from apps.candidate.models import Candidate
from core.extra import generate_otp



def admin_authenticate(email, password, role):
    try:
        user = AdminUser.objects.get(email__iexact=email, roles__contains=[role], active=True, published=True)
        # if user.check_password(password):
        #     return user
        return user
    except ObjectDoesNotExist:
        pass



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

