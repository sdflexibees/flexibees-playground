from django.urls import path
from apps.candidate.mobility_views import CandidateAccountsAPI, CandidateEmailPhoneVerifyAPI, CandidateSignUp
from apps.candidate.views import AllCandidateViewSet
from apps.notifications.views import LogoutAPI




urlpatterns = [
    # candidate mobile
    path('signup/', CandidateAccountsAPI.as_view({'post': 'candidate_sign_up'})),
    path('verify-otp/', CandidateAccountsAPI.as_view({'post': 'verify_otp'})),
    path('candidate-login/', CandidateAccountsAPI.as_view({'post': 'candidate_login'})),
    path('resend-otp/', CandidateAccountsAPI.as_view({'post': 'resend_otp'})),
    path('verify-email-phone/', CandidateEmailPhoneVerifyAPI.as_view({'post': 'candidate_email_phone_verify'})),
    path('email-phone-otp-verify/', CandidateEmailPhoneVerifyAPI.as_view({'post': 'candidate_otp_verify'})),
    
    path('logout/', LogoutAPI.as_view()),
    # new signup 
    path('email-phone-signup/', CandidateSignUp.as_view({'post': 'sign_up'})),
    path('signup-verify-otp/', CandidateSignUp.as_view({'post': 'verify_otp'})),

    path("candidates/list",AllCandidateViewSet.as_view({"get":"list"})),
]
