from django.urls import re_path
from messaging import consumers

# Connects the websocet to it's respective consumer class
websocket_urlpatterns = [
    re_path(r'ws/brordcast-message/(?P<room_id>\d+)/(?P<room_name>[-\w]+)/$', consumers.MessageConsumer.as_asgi()),
]