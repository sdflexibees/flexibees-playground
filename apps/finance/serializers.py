from rest_framework import serializers
from apps.finance.models import BankAccount, Client, ClientInvoice, Consultant, ConsultantInvoice, Contract, SocialMedia


class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMedia
        fields = [
            'facebook_profile',
            'instagram_profile',
            'linkedin_profile',
            'twitter_profile',
            'permit_social_media_tagging'
        ]
    
    
class SocialMediaListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.first_name', read_only=True)  
    class Meta:
        model = SocialMedia
        fields = [
            'id',
            'facebook_profile',
            'instagram_profile',
            'linkedin_profile',
            'twitter_profile',
            'permit_social_media_tagging',
            'active',
            'username'
        ]
        

class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = [
            'pan_card',
            'aadhar_card',
            'account_holder_name',
            'bank_name',
            'account_number',
            'ifsc_code',
            'branch',
            'city',
            'bank_statement_or_cheque',
            'account_type'
        ]
    # def create(self, validated_data):
    #     # Handle any logic for file uploads here
    #     # Ensure you are checking if the files are processed correctly
    #     return BankAccount.objects.create(**validated_data)
    
    
class BankAccountListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.first_name', read_only=True)  
    class Meta:
        model = BankAccount
        fields = [    
            'id',        
            'pan_card',
            'aadhar_card',
            'account_holder_name',
            'bank_name',
            'account_number',
            'ifsc_code',
            'branch',
            'city',
            'bank_statement_or_cheque',
            'account_type',
            'active',
            'username'
        ]
        

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        exclude = [
            'employer',
            'active',
            'created',
            'modified'
        ]

class ConsultantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultant
        fields = [
            'alt_contact_person_name', 
            'alt_contact_person_number',
            'alt_contact_person_relation'
        ]

class ConsultantListSerializer(serializers.ModelSerializer):
    candidate_name = serializers.SerializerMethodField()
    class Meta:
        model = Consultant
        fields = [
            'id', 'candidate', 'candidate_name', 
            'number_of_current_projects'
        ]
    def get_candidate_name(self, obj):
        full_name = f"{obj.candidate.first_name} {obj.candidate.last_name}"  # Concatenate first and last names
        return f"{full_name}"  # Display both first name and full name


class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = [
            'consultant', 'project', 'job', 'client',
            'consultant_amount', 'consultant_aggregate_amount','client_amount',
            'consultant_contract_type', 'client_contract_type','notice_period',
            'signatory_designation',
            'bdm_gross_margin_commission_percentage', 'bdm_lifetime_commission_percentage',
            'director_name', 'director_email',
            'working_hours_per_day','working_days_in_a_week','paid_leaves'        
        ]
        
        
class ContractListSerializer(serializers.ModelSerializer):
    consultant_name = serializers.SerializerMethodField()
    project_name = serializers.CharField(source='project.deal_name', read_only=True)
    job_details = serializers.SerializerMethodField()
    consultant_contract_type_name = serializers.SerializerMethodField()
    client_contract_type_name = serializers.SerializerMethodField()
    class Meta:
        model = Contract
        fields = ['id', 'consultant_name', 'project_name','job_details', 'consultant_contract_type_name', 'client_contract_type_name','consultant_amount', 'client_amount','signatory_designation']
    
    def get_consultant_name(self, obj):
        full_name = f"{obj.consultant.candidate.first_name} {obj.consultant.candidate.last_name}"  # Concatenate first and last names
        return f"{full_name}"  # Display both first name and full name
    
    def get_job_details(self, obj):
        job_role_function = f"{obj.job.function} - {obj.job.role}"  # Concatenate first and last names
        return f"{job_role_function}"  # Display both function and role 
    
    def get_consultant_contract_type_name(self, obj):
        # This will return the display value of consultant_contract_type
        return obj.get_consultant_contract_type_display()
    
    def get_client_contract_type_name(self, obj):
        # This will return the display value of client_contract_type
        return obj.get_client_contract_type_display()

class ConsultantInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultantInvoice
        fields = [
            'contract', 'invoice_number', 'work_description_type',
            'signature', 'time_sheet_from',
            'time_sheet_to', 'time_sheet_hours'
        ]
    def __init__(self, *args, **kwargs):
        # Extract the consultant from the serializer context
        consultant = kwargs.pop('consultant', None)
        super().__init__(*args, **kwargs)

        if consultant:
            # Filter contracts to show only those related to the consultant
            self.fields['contract'].queryset = Contract.objects.filter(consultant=consultant)
    
    
class ClientInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientInvoice
        fields = [
            'contract', 
            'terms_of_payment', 'description_of_services',
            'is_digital_signature_required'
        ]
