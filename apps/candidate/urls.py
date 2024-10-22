from django.urls import path
from apps.availability.views import CandidateAvailabilityAPI
from apps.candidate.mobility_views import CandidateProjectHistoryAPI, ProjectDetailsAPI, CandidateActiveProjectsAPI, \
    CandidateAccountsAPI, CandidateProfileAPI, CandidateSkillsAPI, CandidateRolesAPI, CandidateEmailPhoneVerifyAPI, \
    CandidateDomainsAPI, CandidateSupportAPI, CandidateLanguageAPI, CandidateSelfAssessmentAPI, \
    CandidateInterestStatusAPI, CandidateAssignmentAPI, CandidateInterviewScheduledAPI, BreakAPI, AppVersionAPI, \
    CandidateLifeStyleAPI, CandidateHomePageAPI, TestAPI, ReferralAPI, CandidateSignUp, CandidateCityAPI
from apps.notifications.views import DeviceRegisterAPI, FcmTokenRegister, LogoutAPI, SamplePushAPI, CandidateNotificationAPI




urlpatterns = [
    # candidate mobile
    path('signup/', CandidateAccountsAPI.as_view({'post': 'candidate_sign_up'})),
    path('verify-otp/', CandidateAccountsAPI.as_view({'post': 'verify_otp'})),
    path('candidate-login/', CandidateAccountsAPI.as_view({'post': 'candidate_login'})),
    path('resend-otp/', CandidateAccountsAPI.as_view({'post': 'resend_otp'})),
    path('verify-email-phone/', CandidateEmailPhoneVerifyAPI.as_view({'post': 'candidate_email_phone_verify'})),
    path('email-phone-otp-verify/', CandidateEmailPhoneVerifyAPI.as_view({'post': 'candidate_otp_verify'})),

    path('candidate-profile-update/', CandidateProfileAPI.as_view({'post': 'candidate_profile_update'})),
    path('view-candidate-profile/', CandidateProfileAPI.as_view({'get': 'view_candidate_profile'})),

    path('candidate-profile/', CandidateProfileAPI.as_view({'get': 'candidate_profile'})),
    path('delete-candidate-profile/', CandidateProfileAPI.as_view({'delete': 'delete_candidate_profile'})),

    path('candidate-work-experience-update/', CandidateProfileAPI.as_view({'post': 'candidate_work_experience_update'})),
    path('view-candidate-work-experience/', CandidateProfileAPI.as_view({'get': 'view_candidate_work_experience'})),
    path('delete-candidate-work-experience/<int:work_experience>/', CandidateProfileAPI.as_view({'delete': 'delete_candidate_work_experience'})),

    path('candidate-education-update/', CandidateProfileAPI.as_view({'post': 'candidate_education_update'})),
    path('view-candidate-education/', CandidateProfileAPI.as_view({'get': 'view_candidate_education'})),
    path('delete-candidate-education/<int:education>/', CandidateProfileAPI.as_view({'delete': 'delete_candidate_education'})),

    path('candidate-certification-update/', CandidateProfileAPI.as_view({'post': 'candidate_certification_update'})),
    path('view-candidate-certification/', CandidateProfileAPI.as_view({'get': 'view_candidate_certification'})),
    path('delete-candidate-certification/<int:certification>/', CandidateProfileAPI.as_view({'delete': 'delete_candidate_certification'})),

    path('candidate-language-update/', CandidateProfileAPI.as_view({'post': 'candidate_language_update'})),
    path('view-candidate-language/', CandidateProfileAPI.as_view({'get': 'view_candidate_language'})),
    path('delete-candidate-language/<int:language>/', CandidateProfileAPI.as_view({'delete': 'delete_candidate_language'})),

    path('candidate-attachment-update/', CandidateProfileAPI.as_view({'post': 'candidate_attachment_update'})),
    path('view-candidate-attachment/', CandidateProfileAPI.as_view({'get': 'view_candidate_attachment'})),
    path('delete-candidate-attachment/', CandidateProfileAPI.as_view({'delete': 'delete_candidate_attachment'})),

    path('candidate-other-details-update/', CandidateProfileAPI.as_view({'post': 'candidate_other_details_update'})),
    path('view-candidate-other-details/', CandidateProfileAPI.as_view({'get': 'view_candidate_other_details'})),
    path('delete-candidate-other-details/', CandidateProfileAPI.as_view({'put': 'delete_candidate_other_details'})),

    path('project-history/', CandidateProjectHistoryAPI.as_view({'get': 'candidate_project_history'})),
    path('active-projects/', CandidateActiveProjectsAPI.as_view({'get': 'candidate_active_projects'})),
    path('project-details/<int:project>/', ProjectDetailsAPI.as_view({'get': 'project_details'})),

    path('candidate-skills/', CandidateSkillsAPI.as_view({'post': 'candidate_skills_listing'})),
    path('candidate-roles/', CandidateRolesAPI.as_view({'post': 'candidate_roles_listing'})),
    path('candidate-domains/', CandidateDomainsAPI.as_view({'post': 'candidate_domains_listing'})),
    path('candidate-language/', CandidateLanguageAPI.as_view({'post': 'candidate_language_listing'})),

    path('support/', CandidateSupportAPI.as_view({'post': 'candidate_support'})),
    path('self-assessment/<int:project>/', CandidateSelfAssessmentAPI.as_view({'get': 'candidate_self_assessment'})),
    path('self-assessment-update/<int:project>/', CandidateSelfAssessmentAPI.as_view({'post': 'candidate_self_assessment_update'})),

    path('interest-status-update/<int:project>/', CandidateInterestStatusAPI.as_view({'post': 'candidate_interest_status_update'})),

    path('assignment-upload/<int:project>/', CandidateAssignmentAPI.as_view({'post': 'candidate_assignment_upload'})),
    path('view-assignment/<int:project>/', CandidateAssignmentAPI.as_view({'get': 'view_candidate_assignment'})),

    path('view-scheduled-timing/<int:project>/', CandidateInterviewScheduledAPI.as_view({'post': 'view_scheduled_timing'})),

    path('register-device/', DeviceRegisterAPI.as_view()),
    path('register/device', FcmTokenRegister.as_view()),
    path('logout/', LogoutAPI.as_view()),
    path('sample-push/<int:user>/', SamplePushAPI.as_view()),

    # notification
    path('notification/<int:page_size>/<int:page>/', CandidateNotificationAPI.as_view({'get': 'candidate_notification_list'})),
    path('test/<int:user>/', BreakAPI.as_view({'get': 'get'})),
    path('app-info/', AppVersionAPI.as_view({'get': 'get'})),

    # candidate lifestyle
    path('life-style/', CandidateLifeStyleAPI.as_view({'put': 'update_lifestyle_response'})),
    path('get-life-style/', CandidateLifeStyleAPI.as_view({'get': 'get_lifestyle'})),

    # candidate availability
    path('wakeup-time-update/', CandidateAvailabilityAPI.as_view({'post': 'update_wakeup_time'})),
    path('get-wakeup-time/', CandidateAvailabilityAPI.as_view({'get': 'get_wakeup_time'})),
    path('availability-list/', CandidateAvailabilityAPI.as_view({'post': 'candidate_availability_list'})),
    path('typical-day/', CandidateAvailabilityAPI.as_view({'get': 'candidate_typical_day'})),

    path('home-page/', CandidateHomePageAPI.as_view({'get': 'candidate_home_page'})),
    path('test/', TestAPI.as_view({'get': 'get'})),
    path('update-mobile-app-version/', CandidateHomePageAPI.as_view({'put': 'update_mobile_app_version'})),

    path('add-activity/', CandidateAvailabilityAPI.as_view({'post': 'add_to_timeline'})),
    path('edit-activity/<int:availability_id>/', CandidateAvailabilityAPI.as_view({'post': 'edit_timeline'})),
    path('delete-activity/<int:availability_id>/', CandidateAvailabilityAPI.as_view({'post': 'delete_activity'})),
    path('update-timeline-status/', CandidateAvailabilityAPI.as_view({'put': 'update_timeline_status'})),

    # Referral
    path('referral-text/', ReferralAPI.as_view({'get': 'get_referral_text'})),
    # new signup 
    path('email-phone-signup/', CandidateSignUp.as_view({'post': 'sign_up'})),
    path('signup-verify-otp/', CandidateSignUp.as_view({'post': 'verify_otp'})),
    # country and city dropdown urls
    path('countries-list/', CandidateCityAPI.as_view({'get': 'get_countries'})),
    path('cities-list/<int:country>/', CandidateCityAPI.as_view({'get': 'get_cities'})),
]
