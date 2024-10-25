from django.urls import path

from apps.finance.views import BankAccountAPI, ConsultantAPI, SocialMediaAPI

urlpatterns = [
    path('social-media/', SocialMediaAPI.as_view({'post': 'create'}), name='socialmedia-create'),
    path('social-media/<int:id>/', SocialMediaAPI.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='socialmedia-detail'),  # Combining retrieve, update, and delete
    path('social-media/list/', SocialMediaAPI.as_view({'get': 'list'}), name='socialmedia-list'),
    
    path('bank-account/', BankAccountAPI.as_view({'post': 'create'}), name='bankaccount-create'),
    path('bank-account/<int:id>/', BankAccountAPI.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='bankaccount-detail'),  # Combining retrieve, update, and delete
    path('bank-account/list/', BankAccountAPI.as_view({'get': 'list'}), name='bankaccount-list'),
    
    path('consultant/', ConsultantAPI.as_view({'post': 'create'}), name='consultant-create'),
    path('consultant/<int:id>/', ConsultantAPI.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='consultant-detail'),  # Combining retrieve, update, and delete
    path('consultant/list/', ConsultantAPI.as_view({'get': 'list'}), name='consultant-list'),
]