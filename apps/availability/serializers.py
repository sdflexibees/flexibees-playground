from rest_framework.serializers import ModelSerializer, Serializer, TimeField, SerializerMethodField, IntegerField, \
    ListField, DictField, CharField

from apps.candidate.models import WebUser
from core.model_choices import LIFESTYLE_RESPONSES_CHOICES
from .models import ActivityCard, CandidateAvailability


class ActivityCardSerializer(ModelSerializer):

    class Meta:
        model = ActivityCard
        exclude = ('active', 'modified', )


class ActivityCardListingSerializer(ModelSerializer):

    class Meta:
        model = ActivityCard
        fields = ('id', 'title', 'image', 'description', 'free_time', 'lifestyle_responses',)


class ActivityCardDetailSerializer(ModelSerializer):
    class Meta:
        model = ActivityCard
        fields = ('title', 'image', 'description', 'free_time', 'id',)


class CandidateTimelineSerializer(ModelSerializer):
    activity_card = ActivityCardDetailSerializer()

    class Meta:
        model = CandidateAvailability
        exclude = ('active', 'modified', 'created', 'candidate',)


class CandidateTimelinePDFSerializer(CandidateTimelineSerializer):
    start_time = TimeField(format='%I:%M %p')
    end_time = TimeField(format='%I:%M %p')


class TimelineSerializer(ModelSerializer):

    class Meta:
        model = CandidateAvailability
        exclude = ('active', 'modified', 'created',)


class TimelineDetailSerializer(ModelSerializer):
    activity_card = ActivityCardDetailSerializer()

    class Meta:
        model = CandidateAvailability
        fields = ('id', 'candidate', 'activity_card', 'start_time', 'end_time', 'previous_activity', 'next_activity', )


class AddTimelineSerializerSwagger(ModelSerializer):

    class Meta:
        model = CandidateAvailability
        exclude = ('active', 'modified', 'created', 'start_time', 'previous_activity', 'next_activity',)


class ActivityCardListSerializer(ModelSerializer):
    # sessions = SerializerMethodField('fetch_sessions')
    #
    # @staticmethod
    # def fetch_sessions(instance):
    #     return {session: instance.admin_priority[session] for session in instance.sessions}
    lifestyle_responses = SerializerMethodField('fetch_lifestyle_responses')

    @staticmethod
    def fetch_lifestyle_responses(instance):
        return [{'id': response, 'name': dict(LIFESTYLE_RESPONSES_CHOICES)[response]} for response in
                instance.lifestyle_responses]

    class Meta:
        model = ActivityCard
        fields = ('id', 'title', 'description', 'image', 'sessions', 'free_time', 'lifestyle_responses',
                  'admin_priority')


class EditTimelineSerializerSwagger(Serializer):
    end_time = TimeField(required=True)
    activity_card = IntegerField(required=True)
    new_activities = ListField()

    class Meta:
        model = CandidateAvailability
        exclude = ('active', 'modified', 'created', 'start_time', 'previous_activity', 'next_activity',)


class SearchActivityCardSerializer(ModelSerializer):
    search_term = CharField(default='')
    filter_data = DictField(default={'search_term': '', 'filter_data': {}})

    class Meta:
        model = ActivityCard
        fields = ('search_term', 'filter_data')


class SearchWebUserSerializer(ModelSerializer):
    search_term = CharField(default='')

    class Meta:
        model = WebUser
        fields = ('search_term', )
