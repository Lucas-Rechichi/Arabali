from django.urls import path, include
from messaging import messaging_views
from messaging import ajax_views
urlpatterns = [
    path('chat/', messaging_views.chat_base, name='chat_base'),

    path('create_chat_room/<int:increment>', messaging_views.create_chat_room, name='create_chat_room'),
    path('chat/<str:room>/<int:room_id>', messaging_views.chat_room_view, name='chat_room'),

    path('chat/message-sent-text/', ajax_views.message_sent_text, name='message_sent_text'),
]