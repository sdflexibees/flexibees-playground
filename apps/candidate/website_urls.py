from django.urls import path

from apps.candidate.views import WebUsersRegisterAPI, WebsiteSendLinkAPI

urlpatterns = [
    path('register/', WebUsersRegisterAPI.as_view()),
    path('send-app-links/', WebsiteSendLinkAPI.as_view({'post':'send_app_link'})),
]
