from django.views import View
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from apps.candidate.models import Candidate
from apps.common.models import UserType, Users
from apps.employer.permission_class import EmployerAuthentication
from core.api_permissions import AppUserAuthentication
from core.response_format import message_response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from apps.finance.models import BankAccount, Consultant, ConsultantContract, SocialMedia
from apps.finance.serializers import BankAccountSerializer, ConsultantContractListSerializer, ConsultantContractSerializer, ConsultantListSerializer, ConsultantSerializer, SocialMediaListSerializer, SocialMediaSerializer

from django.template.loader import get_template, render_to_string
from xhtml2pdf import pisa
from django.http import HttpResponse
from rest_framework.permissions import BasePermission
from rest_framework.permissions import IsAuthenticated



class CandidateOrEmployerPermission(BasePermission):
    """
    Custom permission to allow access if the user is authenticated either
    as a candidate (AppUserAuthentication) or as an employer (EmployerAuthentication).
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated by AppUserAuthentication
        app_user_auth = AppUserAuthentication().has_permission(request, view)
        
        # Check if user is authenticated by EmployerAuthentication
        employer_auth = EmployerAuthentication().has_permission(request, view)

        # Allow access if either permission class grants access
        return app_user_auth or employer_auth


class SocialMediaAPI(ModelViewSet):
    serializer_class = SocialMediaSerializer
    permission_classes = [CandidateOrEmployerPermission]  

    @swagger_auto_schema(
        request_body=SocialMediaSerializer,
        operation_description='Create a social media profile',
    )
    def create(self, request):
        """
        Create social media profiles for the logged-in user.
        :param request: Social media profile data
        :return: Response with created profile or error
        """
        user = request.user  
        
        existing_user = Users.objects.filter(email=user.email).first()
        if existing_user:
            user = existing_user
        else: 
            candidate = get_object_or_404(Candidate, id=user.id, active=True)     
            if candidate:
                type, created = UserType.objects.get_or_create(type_name="Candidate")
                new_user = Users(
                                email = user.email, 
                                password = user.password, 
                                first_name = user.first_name, 
                                last_name = user.last_name,
                                type = type,
                                user_type = "2",
                                profile_image = candidate.profile_pic,
                                country_code = candidate.country_code,
                                mobile = candidate.phone,
                                otp = candidate.otp,
                                address = candidate.address,
                                phone_verified = candidate.phone_verified,
                                email_verified = candidate.email_verified,
                                is_active = candidate.active,
                                created_at = candidate.created,
                                updated_at = candidate.modified    
                            )
                # Manually hash and set the password
                new_user.set_password(user.password)

                # Save the new user to the database
                new_user.save()
                user = new_user
                
        # Check if the user already has an active profile
        existing_profile = SocialMedia.objects.filter(user=user, active=True).first()

        if existing_profile:
            # If an active profile exists, return an error
            return Response(message_response("Profile already exists for this user"), status=400)
        else:
            # Assuming the request data contains the social media profile fields directly
            serializer = SocialMediaSerializer(data=request.data, context={'request': request})
            
            if serializer.is_valid():
                serializer.save(user=user)  # Save the profile with the associated user
                return Response(message_response("Profile created successfully"), status=201)
            else:
                return Response(serializer.errors, status=400)

    @swagger_auto_schema(
        operation_description='Retrieve a social media profile by ID',
    )
    def retrieve(self, request, id=None):
        """
        Retrieve social media profile by ID
        :param request: id
        :return: Profile details
        """
        social_media = get_object_or_404(SocialMedia, id=id, active=True)
        serializer = SocialMediaSerializer(social_media)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description='List all active social media profiles',
    )
    def list(self, request):
        """
        List all active social media profiles
        :param request: None
        :return: List of profiles
        """
        social_medias = SocialMedia.objects.filter(active=True).order_by('-id')
        serializer = SocialMediaListSerializer(social_medias, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=SocialMediaSerializer,
        operation_description='Partially update a social media profile',
    )
    def update(self, request, id=None):
        """
        Edit social media profile
        :param request: id and new data
        :return: Updated profile details
        """
        print("request.data ",request.data)
        social_media = get_object_or_404(SocialMedia, id=id, active=True)
        serializer = SocialMediaSerializer(social_media, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @swagger_auto_schema(
        operation_description='Deactivate a social media profile',
    )
    def destroy(self, request, id=None):
        """
        Deactivate social media profile
        :param request: id
        :return: Deactivation message
        """
        social_media = get_object_or_404(SocialMedia, id=id, active=True)
        social_media.active = False
        social_media.save()
        return Response(message_response("Social media profile deactivated successfully"), status=200)
    
    
    
class BankAccountAPI(ModelViewSet):    
    serializer_class = BankAccountSerializer
    permission_classes = [CandidateOrEmployerPermission]

    @swagger_auto_schema(
        request_body=BankAccountSerializer,
        operation_description='Create bank account',
    )
    def create(self, request):
        """
        Create bank accounts for the logged-in user.
        """
        user = request.user  # Get the logged-in user
        print("user ",user)
        existing_user = Users.objects.filter(email=user.email).first()
        if existing_user:
            print("existing user")
            user = existing_user
        else: 
            candidate = get_object_or_404(Candidate, id=user.id, active=True)     
            if candidate:
                print("new user - candidate")
                type, created = UserType.objects.get_or_create(type_name="Candidate")
                new_user = Users(
                                email = user.email, 
                                password = user.password, 
                                first_name = user.first_name, 
                                last_name = user.last_name,
                                type = type,
                                user_type = "2",
                                profile_image = candidate.profile_pic,
                                country_code = candidate.country_code,
                                mobile = candidate.phone,
                                otp = candidate.otp,
                                address = candidate.address,
                                phone_verified = candidate.phone_verified,
                                email_verified = candidate.email_verified,
                                is_active = candidate.active,
                                created_at = candidate.created,
                                updated_at = candidate.modified    
                            )
                # Manually hash and set the password
                new_user.set_password(user.password)

                # Save the new user to the database
                new_user.save()
                user = new_user
        
        # Check if the user already has an active bank account
        existing_bank_account = BankAccount.objects.filter(user=user, active=True).first()
        print("existing bank account ",existing_bank_account)
        if existing_bank_account:
            # If an active bank account exists, return an error response
            return Response(message_response("Bank account already exists for this user"), status=400)
        else:
            print("Bank account not exist")
            # If no bank account exists, proceed with creating a new one        
            serializer = BankAccountSerializer(data=request.data, context={'request': request})
            print("serializer ",serializer)
            if serializer.is_valid():
                print("serializer is valid")
                print("user ",user)
                try:
                    serializer.save(user=user)
                except Exception as e:
                    print(f"Error saving serializer: {e}")
                    return Response({"error": str(e)}, status=500)

                return Response(message_response("Bank accounts created successfully"), status=201)
            return Response(serializer.errors, status=400)  

    @swagger_auto_schema(
        operation_description='Retrieve a bank account by ID',
    )
    def retrieve(self, request, id=None):
        """
        Retrieve bank account by ID
        """
        bank_account = get_object_or_404(BankAccount, id=id, active=True)
        serializer = BankAccountSerializer(bank_account)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description='List all active bank accounts',
    )
    def list(self, request):
        """
        List all active bank accounts
        """
        bank_accounts = BankAccount.objects.filter(active=True).order_by('-id')
        serializer = BankAccountSerializer(bank_accounts, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=BankAccountSerializer,
        operation_description='Partially update a bank account',
    )
    def partial_update(self, request, id=None):
        """
        Edit bank account
        """
        bank_account = get_object_or_404(BankAccount, id=id, active=True)
        serializer = BankAccountSerializer(bank_account, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @swagger_auto_schema(
        operation_description='Deactivate a bank account',
    )
    def destroy(self, request, id=None):
        """
        Deactivate bank account
        """
        bank_account = get_object_or_404(BankAccount, id=id, active=True)
        bank_account.active = False
        bank_account.save()
        return Response(message_response("Bank account deactivated successfully"), status=200)
    
    
class ConsultantAPI(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ConsultantSerializer

    def get_queryset(self):
        return Consultant.objects.filter(active=True).order_by('-id')

    @swagger_auto_schema(operation_description='List all active consultants')
    def list(self, request):
        queryset = self.get_queryset()
        serializer = ConsultantListSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(operation_description='Retrieve consultant details by ID')
    def retrieve(self, request, id=None):
        consultant = get_object_or_404(Consultant, id=id, active=True)
        serializer = ConsultantSerializer(consultant)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ConsultantSerializer, operation_description='Create a new consultant')
    def create(self, request):
        serializer = ConsultantSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(message_response("Consultant created successfully"), status=201)
        return Response(serializer.errors, status=400)

    @swagger_auto_schema(request_body=ConsultantSerializer, operation_description='Update consultant details')
    def partial_update(self, request, id=None):
        consultant = get_object_or_404(Consultant, id=id, active=True)
        serializer = ConsultantSerializer(consultant, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @swagger_auto_schema(operation_description='Deactivate consultant')
    def destroy(self, request, id=None):
        consultant = get_object_or_404(Consultant, id=id, active=True)
        consultant.active = False
        consultant.save()
        return Response(message_response("Consultant deactivated successfully"), status=200)


class ConsultantContractAPI(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ConsultantContract.objects.filter(active=True).order_by('-id')

    @swagger_auto_schema(operation_description='List all active consultant contracts')
    def list(self, request):
        queryset = self.get_queryset()
        serializer = ConsultantContractListSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(operation_description='Retrieve consultant contract details by ID')
    def retrieve(self, request, id=None):
        contract = get_object_or_404(ConsultantContract, id=id, active=True)
        serializer = ConsultantContractSerializer(contract)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ConsultantContractSerializer, operation_description='Create a new consultant contract')
    def create(self, request):
        serializer = ConsultantContractSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Consultant contract created successfully"}, status=201)
        return Response(serializer.errors, status=400)

    @swagger_auto_schema(request_body=ConsultantContractSerializer, operation_description='Update consultant contract details')
    def partial_update(self, request, id=None):
        contract = get_object_or_404(ConsultantContract, id=id, active=True)
        serializer = ConsultantContractSerializer(contract, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @swagger_auto_schema(operation_description='Deactivate consultant contract')
    def destroy(self, request, id=None):
        contract = get_object_or_404(ConsultantContract, id=id, active=True)
        contract.active = False
        contract.save()
        return Response({"message": "Consultant contract deactivated successfully"}, status=200)
    
    
def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('We had some errors while generating the PDF.', status=500)
    
    return response


class GenerateContractPDF(View):
    def get(self, request, id=None):
        # Fetch the contract instance
        contract = get_object_or_404(ConsultantContract, id=id)

        # Define the appropriate template based on contract type
        if contract.contract_type == 'Internal Consultant':
            template_name = 'contracts/FlexiBees_Agreement.html'
        elif contract.contract_type == 'External -Resourcing - Fixed Working Hours':
            template_name = 'contracts/external_contract2_1.html'
        elif contract.contract_type == 'External -Resourcing - Work Basis':
            template_name = 'contracts/external_contract2.html'
        elif contract.contract_type == 'External -Resourcing - Hourly Basis':
            template_name = 'contracts/external_contract1.html'
        elif contract.contract_type == 'External - Placement - One Time Fee':
            template_name = 'contracts/external_consultant_agreement.html'
        else:
            # Default template if no contract type is selected or unknown type
            template_name = 'contracts/external_consultant.html'

        # Prepare the context for rendering the PDF
        context = {
            'candidate_name': contract.candidate_name,
            'client_name': contract.client_name,
            'duration': contract.duration,
            'amount': contract.amount,
            'candidate_address': contract.candidate_address,
            'candidate_email': contract.candidate_email,
            'contract_date': contract.contract_date,
            'commence_date': contract.commence_date,
            'contract_end_date': contract.contract_end_date,
            'flexibees_details': FLEXIBEES_DETAILS,
        }

        # Render the selected template to PDF
        return render_to_pdf(template_name, context)