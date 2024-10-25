from django.conf.urls import url
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.admin_app.views import AdminLoginAPI, RoleAPI, SkillAPI
from ..candidate.views import CandidateDetailAPI

router = DefaultRouter()
router.register(r'skill', SkillAPI, basename='skill'),
router.register(r'role', RoleAPI, basename='role'),


urlpatterns = [  
    path('', include(router.urls)),
    path('login/', AdminLoginAPI.as_view({'post': 'login'})),
    path('candidate-detail/<int:candidate>/', CandidateDetailAPI.as_view({'get': 'retrieve'})),
    path('candidate-detail/<int:candidate>/<int:project>/', CandidateDetailAPI.as_view({'get': 'retrieve'}))
]
