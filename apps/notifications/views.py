import datetime
from asgiref.sync import async_to_sync
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from apps.notifications.consumers import get_notification_count, update_admin, get_candidate_notification_count, \
    update_candidate
from apps.notifications.models import AdminNotification, UserDevice, CandidateNotification
from apps.notifications.serializers import AdminNotificationListSerializer, RegisterDeviceSerializer, \
    CandidateNotificationListSerializer
from core.fcm import send_candidate_notification
from core.pagination import paginate
from core.api_permissions import AdminAuthentication, AppUserAuthentication
from core.response_format import message_response
from core.response_messages import invalid_input, created
from core.validations import check_invalid


def notify_admin(item_type, item_id, sent_by_type, sent_to_type, sent_by, message, sent_to=None):
    AdminNotification.objects.create(item_type=item_type, item_id=item_id, sent_by_type=sent_by_type,
                                     sent_to_type=sent_to_type, sent_by=sent_by, sent_to=sent_to, message=message)
    return True


class CandidateNotificationAPI(ModelViewSet):
    permission_classes = (AppUserAuthentication,)

    @staticmethod
    def candidate_notification_list(request, page=1, page_size=10):
        notifications = list(CandidateNotification.objects.filter(active=True, sent_to=request.user))
        result = paginate(notifications, CandidateNotificationListSerializer, page=page, page_size=page_size,
                          context={'user': request.user})
        notification_ids = [notification['id'] for notification in result['results']]
        request.user.read_notifications = list(set().union(request.user.read_notifications, notification_ids))
        request.user.save()
        notification_data = get_candidate_notification_count(request.user)
        async_to_sync(update_candidate)(notification_data, str(request.user.id), 'new_count')
        return Response(result)


class DeviceRegisterAPI(APIView):
    permission_classes = (AppUserAuthentication,)

    @staticmethod
    @swagger_auto_schema(request_body=RegisterDeviceSerializer)
    def post(request):
        device_type = request.data.get('type')
        registration_id = request.data.get('registration_id')
        check_invalid([device_type, registration_id])
        try:
            active_divice = UserDevice.objects.get(type=device_type, registration_id=registration_id, active=True)
            active_divice.user = request.user
            active_divice.save()
        except Exception:
            active_divice = UserDevice.objects.create(user=request.user, type=device_type, registration_id=registration_id,
                                      active=True)
        UserDevice.objects.filter(user=request.user, active=True).exclude(id__in=[active_divice.id]).update(active=False)
        return Response(message_response('Registered'))

class FcmTokenRegister(APIView):
    @staticmethod
    def post(request):
        from apps.admin_app.views import api_logging

        log_data = ['info|| Fcm token generator']
        log_data.append(f'info|| {datetime.datetime.now()}')
        try:
            device_type = request.data.get('type')
            registration_id = request.data.get('registration_id')
            check_invalid([device_type, registration_id])
            UserDevice.objects.create(type=device_type, registration_id=registration_id,active=True)
            return Response(message_response(created), status=200)
        except Exception as e:
            log_data.append(f'error|| {e}')
            api_logging(log_data)
            return Response(message_response(invalid_input), status=400)


class LogoutAPI(APIView):
    permission_classes = (AppUserAuthentication,)

    @staticmethod
    @swagger_auto_schema(request_body=RegisterDeviceSerializer)
    def post(request):
        device_type = request.data.get('type', None)
        registration_id = request.data.get('registration_id', '')
        check_invalid([device_type])
        try:
            device = UserDevice.objects.filter(user=request.user, type=device_type,
                                               registration_id=registration_id, active=True)
            device.update(active=False)
        except ObjectDoesNotExist:
            return Response(message_response(invalid_input), status=400)
        return Response(message_response('Logged out'))


class SamplePushAPI(APIView):

    @staticmethod
    def get(request, user):
        push_data = {
            'title': 'Test notification',
            'message': 'Test message.',
            'item_type': 'project',
            'item_id': 2,
            # 'activity_type': 'project'
        }
        send_candidate_notification(user, push_data=push_data)
        return Response(message_response('Done'))
