from django.conf.urls import url
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.candidate.mobility_views import AppVersionAPI
from ..candidate.views import CandidateDetailAPI, CandidateResumeDownloadAPI

router = DefaultRouter()


urlpatterns = [    
    path('candidate-detail/<int:candidate>/', CandidateDetailAPI.as_view({'get': 'retrieve'})),
    path('candidate-detail/<int:candidate>/<int:project>/', CandidateDetailAPI.as_view({'get': 'retrieve'}))
]
