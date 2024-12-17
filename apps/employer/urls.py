from django.urls import path

from apps.employer.views import EmployerSignUpLoginViewset, EmployerViewSet, IndividualJobDeatils, JobListViewSet, JobViewSet

urlpatterns = [
    path('signup/', EmployerSignUpLoginViewset.as_view({'post': 'signUp'})),
    path('login/', EmployerSignUpLoginViewset.as_view({'post': 'login'})),
    path('verify/', EmployerSignUpLoginViewset.as_view({'post': 'verify_otp'})),
    path("jobs/list",JobViewSet.as_view({"post":"list"})),
    path("home/jobs",JobViewSet.as_view({"post":"home"})),
    path("individual-job/details", IndividualJobDeatils.as_view({"get":"job_details"})),
    
    path("employers/list",EmployerViewSet.as_view({"get":"list"})),
    path("all-jobs/list",JobListViewSet.as_view({"get":"list"}))
]