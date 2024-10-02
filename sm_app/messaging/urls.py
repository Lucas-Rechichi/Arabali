from django.urls import path, include
from messaging import messaging_views
from messaging import ajax_views
urlpatterns = [
    path('chat/', messaging_views.chat_base, name='chat_base'),

    path('chat_settings/<str:room>/<int:room_id>/', messaging_views.chat_room_settings, name='chat_room_settings'),
    path('<str:room>/<int:room_id>/create_poll/', messaging_views.create_poll, name='create_poll'),
    path('create_chat_room/<int:increment>/', messaging_views.create_chat_room, name='create_chat_room'),
    path('chat/<str:room>/<int:room_id>', messaging_views.chat_room_view, name='chat_room'),

    path('chat/message-sent-text/', ajax_views.message_sent_text, name='message_sent_text'),
    path('chat/message-sent-image/', ajax_views.message_sent_image, name='message_sent_image'),
    path('chat/message-sent-video/', ajax_views.message_sent_video, name='message_sent_video'),
    path('chat/message-sent-audio/', ajax_views.message_sent_audio, name='message_sent_audio'),
    path('chat/edit-message/', ajax_views.edit_message, name='edit_message'),
    path('chat/delete-message/', ajax_views.delete_message, name='delete_message'),
    path('chat/reactions/', ajax_views.reactions, name='reactions'),
    path('chat/message-suggestions/', ajax_views.message_suggestions, name='message_suggestions'),

    path('polls/create-poll/', ajax_views.create_poll, name='create_poll'),
    path('polls/vote-for-poll/', ajax_views.vote_for_poll, name='vote_for_poll'),

    path('chat_settings/change-settings/', ajax_views.change_settings, name='change_settings'),
    path('chat_settings/invite-users/', ajax_views.invite_users, name='invite_users'),
    path('chat_settings/leave-chatroom/', ajax_views.leave_chatroom, name='leave_chatroom'),
    
    path('chat_admin/delete-chatroom/', ajax_views.delete_chatroom, name='delete_chatroom'),
    path('chat_admin/admin-settings/', ajax_views.admin_settings, name='admin_settings'),


]