from django.conf.urls import url
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.admin_app.views import AdminLoginAPI

router = DefaultRouter()

urlpatterns = [  
    path('', include(router.urls)),
    path('login/', AdminLoginAPI.as_view({'post': 'login'})),    
]
