from django.urls import path

from apps.finance.views import BankAccountAPI, ClientAPI, ClientInvoiceAPI, ConsultantAPI, ConsultantInvoiceAPI, ConsultantInvoiceListAPI, ConsultantListAPI, ContractAPI, GenerateClientContractPDF, GenerateClientInvoicePDF, GenerateConsultantContractPDF, GenerateConsultantInvoicePDF, SocialMediaAPI
from apps.projects.views import ProjectViewSet

urlpatterns = [
    path('social-media/', SocialMediaAPI.as_view({'post': 'create'}), name='socialmedia-create'),
    path('social-media/retrieve/<int:pk>/', SocialMediaAPI.as_view({'get': 'retrieve'}), name='socialmedia-retrieve'), 
    path('social-media/update/<int:pk>/', SocialMediaAPI.as_view({'put': 'update'}), name='socialmedia-update'), 
    path('social-media/delete/<int:pk>/', SocialMediaAPI.as_view({'delete': 'destroy'}), name='socialmedia-delete'),     
    path('social-media/list/', SocialMediaAPI.as_view({'get': 'list'}), name='socialmedia-list'),
    
    path('bank-account/', BankAccountAPI.as_view({'post': 'create'}), name='bankaccount-create'),
    path('bank-account/retrieve/<int:pk>/', BankAccountAPI.as_view({'get': 'retrieve'}), name='bankaccount-retrieve'), 
    path('bank-account/update/<int:pk>/', BankAccountAPI.as_view({'put': 'update'}), name='bankaccount-update'), 
    path('bank-account/delete/<int:pk>/', BankAccountAPI.as_view({'delete': 'destroy'}), name='bankaccount-delete'),
    path('bank-account/list/', BankAccountAPI.as_view({'get': 'list'}), name='bankaccount-list'),
    
    path('client/', ClientAPI.as_view({'post': 'create'}), name='client-create'),
    path('client/retrieve/<int:pk>/', ClientAPI.as_view({'get': 'retrieve'}), name='client-retrieve'), 
    path('client/update/<int:pk>/', ClientAPI.as_view({'put': 'update'}), name='client-update'), 
    path('client/delete/<int:pk>/', ClientAPI.as_view({'delete': 'destroy'}), name='client-delete'),    
    path('client/list/', ClientAPI.as_view({'get': 'list'}), name='client-list'),
    
    path('consultant/', ConsultantAPI.as_view({'post': 'create'}), name='consultant-create'),
    path('consultant/retrieve/<int:pk>/', ConsultantAPI.as_view({'get': 'retrieve'}), name='consultant-retrieve'), 
    path('consultant/update/<int:pk>/', ConsultantAPI.as_view({'put': 'update'}), name='consultant-update'), 
    path('consultant/delete/<int:pk>/', ConsultantAPI.as_view({'delete': 'destroy'}), name='consultant-delete'), 
    path('consultant/list/', ConsultantListAPI.as_view({'get': 'list'}), name='consultant-list'),
    
    path('contract/', ContractAPI.as_view({'post': 'create'}), name='consultant-create'),
    path('contract/retrieve/<int:pk>/', ContractAPI.as_view({'get': 'retrieve'}), name='contract-retrieve'), 
    path('contract/update/<int:pk>/', ContractAPI.as_view({'put': 'update'}), name='contract-update'), 
    path('contract/delete/<int:pk>/', ContractAPI.as_view({'delete': 'destroy'}), name='contract-delete'),     
    path('contract/list/', ContractAPI.as_view({'get': 'list'}), name='consultant-list'),
    path('generate/contract/consultant/pdf/<int:pk>/', GenerateConsultantContractPDF.as_view(), name='generate_contract_pdf'),
    path('generate/contract/client/pdf/<int:pk>/', GenerateClientContractPDF.as_view(), name='generate_contract_pdf'),
    
    path('project/list/', ProjectViewSet.as_view({'get': 'list'}), name='project-list'),
    
    path('invoice/consultant/', ConsultantInvoiceAPI.as_view({'post': 'create'}), name='consultant-invoice-create'),
    path('invoice/consultant/retrieve/<int:pk>/', ConsultantInvoiceAPI.as_view({'get': 'retrieve'}), name='consultant-invoice-retrieve'), 
    path('invoice/consultant/update/<int:pk>/', ConsultantInvoiceAPI.as_view({'put': 'update'}), name='consultant-invoice-update'), 
    path('invoice/consultant/delete/<int:pk>/', ConsultantInvoiceAPI.as_view({'delete': 'destroy'}), name='consultant-invoice-delete'),     
    path('invoice/consultant/list/', ConsultantInvoiceListAPI.as_view({'get': 'list'}), name='consultant-invoice-list'),
    path('invoice/consultant/generate/<int:pk>/', GenerateConsultantInvoicePDF.as_view(), name='generate-consultant-invoice'), 
    
    path('invoice/client/', ClientInvoiceAPI.as_view({'post': 'create'}), name='client-invoice-create'),
    path('invoice/client/retrieve/<int:pk>/', ClientInvoiceAPI.as_view({'get': 'retrieve'}), name='client-invoice-retrieve'), 
    path('invoice/client/update/<int:pk>/', ClientInvoiceAPI.as_view({'put': 'update'}), name='client-invoice-update'), 
    path('invoice/client/delete/<int:pk>/', ClientInvoiceAPI.as_view({'delete': 'destroy'}), name='client-invoice-delete'),     
    path('invoice/client/list/', ClientInvoiceAPI.as_view({'get': 'list'}), name='client-invoice-list'),
    path('invoice/client/generate/<int:pk>/', GenerateClientInvoicePDF.as_view(), name='generate-client-invoice')  
]