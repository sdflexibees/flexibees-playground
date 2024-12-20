from .wsgi import *
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from apps.notifications.consumers import AdminNotificationConsumer, CandidateNotificationConsumer

channel_routing = [
    path("ws/admin-notification/<str:token>/", AdminNotificationConsumer.as_asgi()),
    path("ws/candidate-notification/<str:token>/", CandidateNotificationConsumer.as_asgi())
]


class RouteNotFoundMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        try:
            return await self.app(scope, receive, send)
        except ValueError as e:
            if (
                "No route found for path" in str(e)
                and scope["type"] == "websocket"
            ):
                await send({"type": "websocket.close"})
                # logger.warning(e)
            else:
                raise e


application = ProtocolTypeRouter({
    "websocket": RouteNotFoundMiddleware(URLRouter(channel_routing)),
})
