from io import BytesIO
from django.views import View
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from apps.candidate.models import Candidate
from apps.common.models import UserType, Users
from apps.employer.models import Employer
from apps.employer.permission_class import EmployerAuthentication
from apps.finance.tasks import send_mail_contract
from core.api_permissions import AdminAuthentication, AppUserAuthentication
from core.response_format import message_response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from apps.finance.models import BankAccount, Client, Consultant, Contract, SocialMedia
from apps.finance.serializers import BankAccountListSerializer, BankAccountSerializer, ClientSerializer, ContractListSerializer, ContractSerializer, ConsultantListSerializer, ConsultantSerializer, SocialMediaListSerializer, SocialMediaSerializer

from django.template.loader import get_template, render_to_string
from xhtml2pdf import pisa
from django.http import HttpResponse
from rest_framework.permissions import BasePermission
from rest_framework.permissions import IsAuthenticated
from weasyprint import HTML
from django.core.exceptions import ValidationError
from rest_framework import status
from django.utils.html import strip_tags


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
    def retrieve(self, request, pk=None):
        """
        Retrieve social media profile by ID
        :param request: id
        :return: Profile details
        """
        social_media = get_object_or_404(SocialMedia, id=pk, active=True)
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
    def update(self, request, pk=None):
        """
        Edit social media profile
        :param request: id and new data
        :return: Updated profile details
        """
        print("request.data ",request.data)
        social_media = get_object_or_404(SocialMedia, id=pk, active=True)
        serializer = SocialMediaSerializer(social_media, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @swagger_auto_schema(
        operation_description='Deactivate a social media profile',
    )
    def destroy(self, request, pk=None):
        """
        Deactivate social media profile
        :param request: id
        :return: Deactivation message
        """
        social_media = get_object_or_404(SocialMedia, id=pk, active=True)
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
    def retrieve(self, request, pk=None):
        """
        Retrieve bank account by ID
        """
        bank_account = get_object_or_404(BankAccount, id=pk, active=True)
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
        serializer = BankAccountListSerializer(bank_accounts, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=BankAccountSerializer,
        operation_description='Partially update a bank account',
    )
    def update(self, request, pk=None):
        """
        Edit bank account
        """
        bank_account = get_object_or_404(BankAccount, id=pk, active=True)
        serializer = BankAccountSerializer(bank_account, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @swagger_auto_schema(
        operation_description='Deactivate a bank account',
    )
    def destroy(self, request, pk=None):
        """
        Deactivate bank account
        """
        bank_account = get_object_or_404(BankAccount, id=pk, active=True)
        bank_account.active = False
        bank_account.save()
        return Response(message_response("Bank account deactivated successfully"), status=200)
    

class ClientAPI(ModelViewSet):
    permission_classes = [EmployerAuthentication]
    serializer_class = ClientSerializer

    def get_queryset(self):
        return Client.objects.all().order_by('-id')

    @swagger_auto_schema(operation_description='List all active clients')
    def list(self, request):
        queryset = self.get_queryset()
        serializer = ClientSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(operation_description='Retrieve client details by ID')
    def retrieve(self, request, pk=None):
        client = get_object_or_404(Client, id=pk, active=True)
        serializer = ClientSerializer(client)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ClientSerializer, operation_description='Create a new client')
    def create(self, request):
        serializer = ClientSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                user=request.user
                employer = Employer.objects.get(user=user)
                social_media = SocialMedia.objects.get(user=user)
                # Save client with the associated employer
                serializer.save(employer=employer,social_media=social_media)
                return Response({"message": "Client created successfully"}, status=status.HTTP_201_CREATED)

            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": "An error occurred while creating the client: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(request_body=ClientSerializer, operation_description='Update client details')
    def update(self, request, pk=None):
        client = get_object_or_404(Client, id=pk, active=True)
        serializer = ClientSerializer(client, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @swagger_auto_schema(operation_description='Deactivate client')
    def destroy(self, request, pk=None):
        client = get_object_or_404(Client, id=pk, active=True)
        client.active = False
        client.save()
        return Response(message_response("Client deactivated successfully"), status=200)
    

class ConsultantAPI(ModelViewSet):
    # permission_classes = [AdminAuthentication]
    serializer_class = ConsultantSerializer

    def get_queryset(self):
        return Consultant.objects.all().order_by('-id')

    @swagger_auto_schema(operation_description='List all active consultants')
    def list(self, request):
        queryset = self.get_queryset()
        serializer = ConsultantListSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(operation_description='Retrieve consultant details by ID')
    def retrieve(self, request, pk=None):
        consultant = get_object_or_404(Consultant, id=pk, active=True)
        serializer = ConsultantSerializer(consultant)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ConsultantSerializer, operation_description='Create a new consultant')
    def create(self, request):
        serializer = ConsultantSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                candidate = serializer.validated_data['candidate']
                # Validate if candidate is active and status is '17'
                if not candidate.active or candidate.status != '17':
                    return Response({"error": "Candidate is either inactive or does not meet status requirements."}, status=status.HTTP_400_BAD_REQUEST)                
                
                existing_user = Users.objects.filter(email=candidate.email).first()
                if existing_user:
                    print("user already exists ",existing_user)
                    user = existing_user                
                else:
                    # If candidate doesn't have an associated user, create one
                    if candidate:
                        print("user is a candidate")
                        type, created = UserType.objects.get_or_create(type_name="Candidate")
                        new_user = Users(
                            email=candidate.email,
                            first_name=candidate.first_name,
                            last_name=candidate.last_name,
                            type=type,
                            user_type="2",
                            profile_image=candidate.profile_pic,
                            country_code=candidate.country_code,
                            mobile=candidate.phone,
                            otp=candidate.otp,
                            address=candidate.address,
                            phone_verified=candidate.phone_verified,
                            email_verified=candidate.email_verified,
                            is_active=candidate.active,
                            created_at=candidate.created,
                            updated_at=candidate.modified    
                        )
                        # Manually set password
                        new_user.set_password(candidate.password)
                        new_user.save()
                        print("new user saved")
                        user = new_user
                # Save consultant with the associated user
                serializer.save(user=user)
                return Response({"message": "Consultant created successfully"}, status=status.HTTP_201_CREATED)

            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": "An error occurred while creating the consultant: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(request_body=ConsultantSerializer, operation_description='Update consultant details')
    def update(self, request, pk=None):
        consultant = get_object_or_404(Consultant, id=pk, active=True)
        serializer = ConsultantSerializer(consultant, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @swagger_auto_schema(operation_description='Deactivate consultant')
    def destroy(self, request, pk=None):
        consultant = get_object_or_404(Consultant, id=pk, active=True)
        consultant.active = False
        consultant.save()
        return Response(message_response("Consultant deactivated successfully"), status=200)


class ContractAPI(ModelViewSet):
    # permission_classes = [AdminAuthentication]
    serializer_class = ContractSerializer

    def get_queryset(self):
        return Contract.objects.filter(active=True).order_by('-id')

    @swagger_auto_schema(operation_description='List all active consultant contracts')
    def list(self, request):
        queryset = self.get_queryset()
        serializer = ContractListSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(operation_description='Retrieve consultant contract details by ID')
    def retrieve(self, request, pk=None):
        contract = get_object_or_404(Contract, id=pk, active=True)
        serializer = ContractSerializer(contract)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ContractSerializer, operation_description='Create a new consultant contract')
    def create(self, request):
        serializer = ContractSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():  
            serializer.save()
            return Response({"message": "Contract created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=400)

    @swagger_auto_schema(request_body=ContractSerializer, operation_description='Update consultant contract details')
    def update(self, request, pk=None):
        contract = get_object_or_404(Contract, id=pk, active=True)
        serializer = ContractSerializer(contract, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @swagger_auto_schema(operation_description='Deactivate consultant contract')
    def destroy(self, request, pk=None):
        contract = get_object_or_404(Contract, id=pk, active=True)
        contract.active = False
        contract.save()
        return Response({"message": "Contract deactivated successfully"}, status=200)

    
def render_to_pdf(template_src, context_dict, filename):
    template = get_template(template_src)
    html_content = template.render(context_dict)
    # response = HttpResponse(content_type='application/pdf')
    # pisa_status = pisa.CreatePDF(html_content, dest=response)
    
    # if pisa_status.err:
    #     return HttpResponse('We had some errors while generating the PDF.', status=500)
    # Create a PDF from the rendered HTML content
    pdf_file = HTML(string=html_content).write_pdf()

    # Serve the PDF as a downloadable file
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    return response


class GenerateConsultantContractPDF(View):
    def get(self, request, pk=None):
        # Fetch the contract instance
        contract = get_object_or_404(Contract, id=pk)
        
        # Define the appropriate template and filename based on contract type
        if contract.consultant_contract_type == '1':
            template_name = 'contracts/consultant/external_consultant_contract+side_letter.html'
            filename = f"{contract.consultant.candidate.first_name}_{contract.consultant.candidate.last_name}_FlexiBees_{contract.client.legal_entity_name}.pdf"
        elif contract.consultant_contract_type == '2':
            template_name = 'contracts/consultant/internal_bd_contract+side_letter+nda.html'
            filename = f"{contract.consultant.candidate.first_name}_{contract.consultant.candidate.last_name}_FlexiBees_Agreement & NDA.pdf"
        else:
            template_name = 'contracts/consultant/internal_consultant_non_bdm.html'
            filename = f"{contract.consultant.candidate.first_name}_{contract.consultant.candidate.last_name}_FlexiBees_Agreement & NDA.pdf"
        
        user = contract.consultant.user
        print("consultant user ",user)
        bank_account = BankAccount.objects.get(user=user)
        # Prepare the context for rendering the PDF
        context = {
            'candidate': contract.consultant.candidate,
            'client':contract.client,
            'client_name': contract.job.employer.user.first_name,
            'consultant_amount': contract.consultant_amount,
            'candidate_address': contract.consultant.candidate.address,
            'candidate_email': contract.consultant.candidate.email,
            'contract_date': contract.created,
            'bank_account':bank_account,
            'job': contract.job,
            'contract_date': contract.created,
            'notice_period':contract.notice_period,
            'bdm_gross_margin_commission_percentage':contract.bdm_gross_margin_commission_percentage,
            'bdm_lifetime_commission_percentage':contract.bdm_lifetime_commission_percentage,
            'contract':contract,
            'director_name_display': contract.get_director_name_display(),
            
        }

        # Render the selected template to PDF
        return render_to_pdf(template_name, context, filename)
    
class GenerateClientContractPDF(View):
    def get(self, request, pk=None):
        # Fetch the contract instance
        contract = get_object_or_404(Contract, id=pk)
        # template_name = 'contracts/client/msw/msw.html'

        # Define the appropriate template based on contract type
        if contract.client_contract_type == '1':
            template_name = 'contracts/client/International_Client Name_FlexiBees_Agreement_&_SOW_Role_Role Name_Consultant Name.html'
        elif contract.client_contract_type == '2':
            template_name = 'contracts/client/Domestic_Proprietorship_Client Name_FlexiBees_Master_Flexi_Staffing_Agreement.html'
        elif contract.client_contract_type == '3':
            template_name = 'contracts/client/Domestic_Non_Proprietorship_Client Name_FlexiBees_Master_Flexi_Staffing_Agreement.html'
        elif contract.client_contract_type == '4':
            template_name = 'contracts/client/Full_Time_Placement_Client Name_Master_Flexi_Staffing_Agreement_SOW.html'
        elif contract.client_contract_type == '5':
            template_name = 'contracts/client/Part_Time_Placement_Client Name_Master_Flexi_Staffing_Agreement_SOW.html'

        # Define the filename for the client contract
        filename = (f"{contract.client.legal_entity_name}_FlexiBees_Agreement & SOW_Role_"
                    f"{contract.job.role}_{contract.consultant.candidate.first_name}_{contract.consultant.candidate.last_name}.pdf")

        # Prepare the context for rendering the PDF
        context = {
            'director_name_display': contract.get_director_name_display(),
            'contract': contract
        }

        # Render the selected template to PDF
        return render_to_pdf(template_name, context, filename)
    

class EmailConsultantContractView(View):
    def post(self, request, pk):
        try:
            # Fetch the contract instance
            contract = get_object_or_404(Contract, pk=pk)
            candidate_name = contract.candidate_name
            month = contract.contract_date.strftime("%B %Y")

            # Generate contract PDF using GenerateConsultantContractPDF
            pdf_view = GenerateConsultantContractPDF.as_view()
            pdf_response = pdf_view(request, pk=contract.id)
            if not isinstance(pdf_response, HttpResponse) or pdf_response.status_code != 200:
                return Response({"error": "Error generating PDF"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Get PDF content
            contract_pdf_content = pdf_response.content
            contract_pdf_bytes = BytesIO(contract_pdf_content)
            candidate_name_with_underscores = candidate_name.replace(' ', '_')
            contract_filename = f"contract_{candidate_name_with_underscores}_{month}.pdf"

            # Prepare email content
            subject = f'Contract for {candidate_name} - {month}'
            html_message = render_to_string('contracts/contract_template.html', context={'contract': contract})
            plain_message = strip_tags(html_message)
            from_email = 'from@example.com'
            to_email = contract.candidate_email

            # Send email asynchronously with Celery
            send_mail_contract.delay(
                subject,
                plain_message,
                html_message,
                from_email,
                to_email,
                contract_filename,
                contract_pdf_bytes.getvalue()
            )

            return Response({"message": "Email sent successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
