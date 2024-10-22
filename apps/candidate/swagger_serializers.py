from rest_framework.serializers import Serializer, ModelSerializer, CharField, IntegerField, ListField

from apps.availability.models import ActivityCard
from apps.candidate.models import Candidate


class LoginSerializer(ModelSerializer):

    class Meta:
        model = Candidate
        fields = ('email', 'country_code', 'phone')


class SignupSerializer(ModelSerializer):
    signup_method = CharField(required=True)

    class Meta:
        model = Candidate
        fields = ('email', 'country_code', 'phone', 'signup_method', 'first_name', 'last_name')


class VerifyOTPSerializer(ModelSerializer):
    user_id = IntegerField(required=True)
    otp = CharField(source='password')

    class Meta:
        model = Candidate
        fields = ('user_id', 'otp')


class ActivityListSerializer(Serializer):
    session = CharField(default='morning')


class WakeupTimeSerializer(ModelSerializer):
    new_activities = ListField()

    class Meta:
        model = Candidate
        fields = ('wakeup_time', 'new_activities',)


class UpdateTimelineStatusSerializer(ModelSerializer):

    class Meta:
        model = Candidate
        fields = ('timeline_completed', )

