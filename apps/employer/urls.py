from django.urls import path
from apps.employer.views import DraftJobViewset, EmployerSignUpLoginViewset, JobMatchingCandidates, JobViewSet, ProfileUpdateViewset, JobCreationFunctionList, \
    JobCreationRolesList, JobCreationSkillsList, EmployerDomainList, EmployerCandidateRecommendation, EmployerSignUpLoginViewset, JobCandidate, CandidateFeedback, \
    JobPostingCreateViewset, JobCreationSkillsSearchTermList, JobDescriptionAPIGenerator,JobDynamicQuestionsList, IndividualJobDeatils, EmployerJobNotesUpdateCreate, \
    EmployerSlotTimeInterview, EmployerAllStatusList, CandidateViewFeedBack, EmployerSupportAPI


urlpatterns = [
    path('signup/', EmployerSignUpLoginViewset.as_view({'post': 'signUp'})),
    path('verify/', EmployerSignUpLoginViewset.as_view({'post': 'verify_otp'})),
    path('login/', EmployerSignUpLoginViewset.as_view({'post': 'login'})),
    path('deactivate', ProfileUpdateViewset.as_view({'get': 'deactivate'})),
    path('update-profile/', ProfileUpdateViewset.as_view({'post': 'updateProfileDetails'})),
    path('change-mobile/', ProfileUpdateViewset.as_view({'post': 'change_mobile'})),
    path('profile', ProfileUpdateViewset.as_view({'get': 'getProfileDetails'})),
    path('logout', ProfileUpdateViewset.as_view({'get': 'logout'})),
    path('employer-function/list/',JobCreationFunctionList.as_view({'get': 'function_list'})),
    path('employer-role/list/',JobCreationRolesList.as_view({'get': 'roles_list'})),
    path('employer-skill/list/',JobCreationSkillsList.as_view({'get': 'skills_list'})),
    path('skill-search/list/',JobCreationSkillsSearchTermList.as_view({'get': 'skills_list'})),
    path('job/draft/',DraftJobViewset.as_view({'post': 'update'})),
    path('job/draft/<int:id>',DraftJobViewset.as_view({'get': 'retrive'})),
    path('job/draft/<int:id>',DraftJobViewset.as_view({'delete': 'delete'})),
    path('job/draft/list',DraftJobViewset.as_view({'post': 'list'})),
    path('employer-domain/list/',EmployerDomainList.as_view({'get': 'domain_list'})),
    path("candidate-recommendation/list/",EmployerCandidateRecommendation.as_view({"post":"recommendation_list"})),
    path("job-creation/",JobPostingCreateViewset.as_view({"post":"job_creation"})),
    path("jobs/list",JobViewSet.as_view({"post":"list"})),
    path("home/jobs",JobViewSet.as_view({"post":"home"})),
    path("job-description/generator/",JobDescriptionAPIGenerator.as_view({"post":"job_description"})),
    path("job-question/list/",JobDynamicQuestionsList.as_view({"get":"get_question"})),
    path("job/matching-candidates/<int:id>", JobMatchingCandidates.as_view({"post":"matching_candidates"})),
    path("individual-job/details", IndividualJobDeatils.as_view({"get":"job_details"})),
    path("job/skip", JobCandidate.as_view({"post":"skip"})),
    path("candidates/job-notes/",EmployerJobNotesUpdateCreate.as_view({"post":"update_or_create"})),
    path("employer-interview/slot/",EmployerSlotTimeInterview.as_view({"post":"employer_slot_time_interview"})),
    path("employer-status/list/",EmployerAllStatusList.as_view({"get":"status_list"})),
    path("job/shortlist/<int:job>/",CandidateFeedback.as_view({"get":"get_candidates"})),
    path("job/update-feedback/",CandidateFeedback.as_view({"post":"update_feedback"})),
    path("job/candidate/feedback/", CandidateViewFeedBack.as_view({"post":"view_feedback"})),
    path("support", EmployerSupportAPI.as_view({"post":"employer_support"}))

]