from django.conf.urls import url
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.admin_app.views import AdminLoginAPI, RoleAPI, SkillAPI
from apps.candidate.all_candidate import CandidateAPI, CandidateList
from apps.projects.views import AllProjectCountAPI, ProjectAPI, ProjectInfoAPI
from ..candidate.views import CandidateDetailAPI

router = DefaultRouter()
router.register(r'skill', SkillAPI, basename='skill'),
router.register(r'role', RoleAPI, basename='role'),
router.register(r'project', ProjectAPI, basename='project'),


urlpatterns = [  
    path('', include(router.urls)),
    path('login/', AdminLoginAPI.as_view({'post': 'login'})),
    
    # candidate
    path('all-candidates/<int:project>/<int:page_size>/<int:page>/', CandidateList.as_view({'post': 'project_all_candidate_list'})),
    path('candidate-detail/<int:candidate>/', CandidateDetailAPI.as_view({'get': 'retrieve'})),
    path('candidate-detail/<int:candidate>/<int:project>/', CandidateDetailAPI.as_view({'get': 'retrieve'})),
    path('all-candidates-list/<int:page_size>/<int:page>/', CandidateList.as_view({'post': 'all_candidates_list'})),
    path('all-candidates-city-list/<int:page_size>/<int:page>/', CandidateAPI.as_view({'post': 'candidate_city_list'})),
    
    # All projects
    path('all-project-count/', AllProjectCountAPI.as_view({'get': 'all_project_count'})),
    path('project-info/<int:project>/', ProjectInfoAPI.as_view({'get': 'project_info'})),

]
