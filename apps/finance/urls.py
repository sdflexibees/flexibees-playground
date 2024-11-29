from django.urls import path

from apps.finance.views import BankAccountAPI, ClientAPI, ConsultantAPI, ContractAPI, GenerateClientContractPDF, GenerateConsultantContractPDF, SocialMediaAPI
from apps.projects.views import ProjectViewSet

urlpatterns = [
    path('social-media/', SocialMediaAPI.as_view({'post': 'create'}), name='socialmedia-create'),
    path('social-media/<int:id>/', SocialMediaAPI.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='socialmedia-detail'),  # Combining retrieve, update, and delete
    path('social-media/list/', SocialMediaAPI.as_view({'get': 'list'}), name='socialmedia-list'),
    
    path('bank-account/', BankAccountAPI.as_view({'post': 'create'}), name='bankaccount-create'),
    path('bank-account/<int:id>/', BankAccountAPI.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='bankaccount-detail'),  # Combining retrieve, update, and delete
    path('bank-account/list/', BankAccountAPI.as_view({'get': 'list'}), name='bankaccount-list'),
    
    path('client/', ClientAPI.as_view({'post': 'create'}), name='client-create'),
    path('client/<int:pk>/', ClientAPI.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='client-detail'),  # Combining retrieve, update, and delete
    path('client/list/', ClientAPI.as_view({'get': 'list'}), name='client-list'),
    
    path('consultant/', ConsultantAPI.as_view({'post': 'create'}), name='consultant-create'),
    path('consultant/<int:pk>/', ConsultantAPI.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='consultant-detail'),  # Combining retrieve, update, and delete
    path('consultant/list/', ConsultantAPI.as_view({'get': 'list'}), name='consultant-list'),
    
    path('contract/', ContractAPI.as_view({'post': 'create'}), name='consultant-create'),
    path('contract/<int:id>/', ContractAPI.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='consultant-detail'),  # Combining retrieve, update, and delete
    path('contract/list/', ContractAPI.as_view({'get': 'list'}), name='consultant-list'),
    path('generate/contract/consultant/pdf/<int:pk>/', GenerateConsultantContractPDF.as_view(), name='generate_contract_pdf'),
    path('generate/contract/client/pdf/<int:pk>/', GenerateClientContractPDF.as_view(), name='generate_contract_pdf'),
    
    path('project/list/', ProjectViewSet.as_view({'get': 'list'}), name='project-list')    
]