from django.urls import re_path
from messaging import consumers

# Connects the websocket to it's respective consumer class
websocket_urlpatterns = [
    re_path(r'ws/brordcast-message/', consumers.NotificationConsumer.as_asgi()),
    re_path(r'ws/realtime-message-manager/(?P<room_id>\d+)', consumers.MessageConsumer.as_asgi()),
]