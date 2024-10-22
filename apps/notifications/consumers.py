import json

from asgiref.sync import async_to_sync
from channels.exceptions import StopConsumer
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from django.apps import apps
from django.db.models import Q

from apps.admin_app.models import AdminUser
from apps.candidate.models import Candidate
from core.encryption import crypto_decode, jwt_decode_handler


def get_notification_count(user, role):
    notifications = list(apps.get_model('notifications.AdminNotification').objects.
                         filter(active=True).filter(
        Q(Q(sent_to_type=role) & Q(sent_to=user)) |
        (Q(sent_to_type=role) & Q(sent_to=None))
    ).values_list('id', flat=True))
    notifications = list(set(notifications))
    unread_notifications = len(notifications) - len(list(set(user.read_notifications).intersection(notifications)))
    return {
        'unread_count': unread_notifications,
    }


def get_candidate_notification_count(user):
    notifications = list(apps.get_model('notifications.CandidateNotification').objects.
                         filter(active=True, sent_to=user).values_list('id', flat=True))
    notifications = list(set(notifications))
    unread_notifications = len(notifications) - len(list(set(user.read_notifications).intersection(notifications)))
    return {
        'unread_count': unread_notifications,
    }


class AdminNotificationConsumer(WebsocketConsumer):

    def connect(self):
        token = str(self.scope['url_route']['kwargs']['token'])
        try:
            user_id = crypto_decode(jwt_decode_handler(token)['ai'])
            pwd = crypto_decode(jwt_decode_handler(token)['bi']) if jwt_decode_handler(token)['bi'] != '' else ''
            role = jwt_decode_handler(token).get('ci', '')
            user = AdminUser.objects.get(id=int(user_id), password=pwd, active=True, roles__contains=[role])
            self.room_group_name = role + user_id

            # Join chat thread
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            async_to_sync(self.accept())
            data = get_notification_count(user, role)
            self.send(json.dumps(data))
        except:
            self.close()

    def disconnect(self, close_code):
        # Leave event
        try:
            async_to_sync(self.channel_layer.group_discard)(
                self.room_group_name,
                self.channel_name
            )
            raise StopConsumer()
        except:
            pass

    # Receive message from WebSocket
    def receive(self, text_data):
        pass

    # Push new count
    def new_count(self, content):
        # Send message to WebSocket
        self.send(text_data=json.dumps(content['content']))


async def update_admin(data, room, update_type):
    await get_channel_layer().group_send(room, {
        # This "type" defines which handler on the Consumer gets
        # called.
        "type": update_type,
        "content": data,
    })


class CandidateNotificationConsumer(WebsocketConsumer):

    def connect(self):
        token = str(self.scope['url_route']['kwargs']['token'])
        try:
            user_id = crypto_decode(jwt_decode_handler(token)['ai'])
            pwd = crypto_decode(jwt_decode_handler(token)['bi']) if jwt_decode_handler(token)['bi'] != '' else ''
            user = Candidate.objects.get(id=int(user_id), password=pwd, active=True)
            self.room_group_name = str(user_id)

            # Join chat thread
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            async_to_sync(self.accept())
            data = get_candidate_notification_count(user)
            self.send(json.dumps(data))
        except:
            self.close()
            pass

    def disconnect(self, close_code):
        # Leave event
        try:
            async_to_sync(self.channel_layer.group_discard)(
                self.room_group_name,
                self.channel_name
            )
            raise StopConsumer()
        except:
            pass

    # Receive message from WebSocket
    def receive(self, text_data):
        pass

    # Push new count
    def new_count(self, content):
        # Send message to WebSocket
        self.send(text_data=json.dumps(content['content']))


async def update_candidate(data, room, update_type):
    await get_channel_layer().group_send(room, {
        # This "type" defines which handler on the Consumer gets
        # called.
        "type": update_type,
        "content": data,
    })
