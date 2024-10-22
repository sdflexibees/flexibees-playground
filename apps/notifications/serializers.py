from rest_framework.serializers import ModelSerializer, CharField, SerializerMethodField

from .models import AdminNotification, UserDevice, CandidateNotification


class AdminNotificationListSerializer(ModelSerializer):
    admin_type = CharField(source='get_sent_by_type_display')
    sent_by = CharField(source='sent_by.first_name')
    is_read = SerializerMethodField('fetch_is_read')

    def fetch_is_read(self, instance):
        read_notifications = self.context.get('user').read_notifications
        return True if instance.id in read_notifications else False

    class Meta:
        model = AdminNotification
        fields = ('created', 'admin_type', 'sent_by', 'message', 'is_read', 'id',)


class RegisterDeviceSerializer(ModelSerializer):

    class Meta:
        model = UserDevice
        fields = ('type', 'registration_id',)


class CandidateNotificationListSerializer(ModelSerializer):
    is_read = SerializerMethodField('fetch_is_read')

    def fetch_is_read(self, instance):
        read_notifications = self.context.get('user').read_notifications
        return instance.id in read_notifications

    class Meta:
        model = CandidateNotification
        fields = ('created', 'item_type', 'item_id', 'all', 'message', 'id', 'is_read', )
