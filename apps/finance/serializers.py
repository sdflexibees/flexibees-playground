from rest_framework import serializers

from apps.finance.models import BankAccount, Consultant, ConsultantContract, SocialMedia

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
    def create(self, validated_data):
        # Handle any logic for file uploads here
        # Ensure you are checking if the files are processed correctly
        return BankAccount.objects.create(**validated_data)
    
    
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
        
        
class ConsultantSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.first_name', read_only=True)
    social_media = SocialMediaSerializer()
    bank_details = BankAccountSerializer()

    class Meta:
        model = Consultant
        fields = [
            'candidate', 'candidate_name', 'social_media', 'bank_details',
            'alt_contact_person_name', 'alt_contact_person_number',
            'alt_contact_person_relation', 'number_of_projects',
            'number_of_current_projects'
        ]

class ConsultantListSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.first_name', read_only=True)
    class Meta:
        model = Consultant
        fields = [
            'id', 'candidate', 'candidate_name', 'number_of_projects',
            'number_of_current_projects', 'active'
        ]
        

class ConsultantContractSerializer(serializers.ModelSerializer):
    consultant_name = serializers.CharField(source='consultant.candidate.first_name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)

    class Meta:
        model = ConsultantContract
        fields = [
            'id', 'consultant', 'consultant_name', 'project', 'project_name',
            'job', 'job_title', 'contract_type', 'notice_period', 'created_date',
            'signed_date', 'start_date', 'end_date', 'food_allowance', 
            'travel_allowance', 'phone_allowance', 'other_allowance'
        ]
        
        
class ConsultantContractListSerializer(serializers.ModelSerializer):
    consultant_name = serializers.CharField(source='consultant.candidate.first_name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = ConsultantContract
        fields = ['id', 'consultant_name', 'project_name', 'contract_type', 'start_date', 'end_date']

