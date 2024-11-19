from rest_framework import serializers
from .models import Employer, Job

class EmployerSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.first_name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = Employer
        fields = ['id', 'status', 'additional_info', 'is_active', 'created_at', 'updated_at', 'user_name', 'company_name']
        

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'  