import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sm_app.settings')
import django
django.setup()

import json
import pytz
from datetime import datetime
from urllib.parse import unquote
from main.models import UserStats, Notification
from messaging.extras import replace_spaces
from messaging.models import ChatRoom, Message
from django.contrib.auth.models import User
from django.middleware.csrf import get_token

from channels.generic.websocket import WebsocketConsumer

from asgiref.sync import async_to_sync


class MessageConsumer(WebsocketConsumer):
    def connect(self):
        # Collects relevant information about the chatroom.
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        user = self.scope["user"]

        # Getting relevant database objects
        chat_room = ChatRoom.objects.get(id=self.room_id)
        user_stats = UserStats.objects.get(user=user)

        # Defining the room name
        self.room_group_name = f'chat_room_{self.room_id}_{replace_spaces(string=chat_room.name, replacement="_")}'

        # Checking to see if this user has been invited to the chatroom.
        if chat_room.users.filter(user=user_stats.user).exists():
            # Add the user to the channel layer
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            # Accept the WebSocket connection
            self.accept()
        else:
            # Take action if the user is not on the specific page or is not allowed in the chatroom
            self.close(code=4001)  # Close the connection with a custom error code

    def disconnect(self, close_code):
        # Remove the WebSocket from the group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        # Accessing sent data
        text_data_json = json.loads(text_data)
        message = text_data_json['text']
        message_type = text_data_json['message_type']
        message_id = text_data_json['message_id']
        is_reply = text_data_json['is_reply']
        user = self.scope.get("user")  # Use get to safely get the user who is on the page
        if is_reply == 'true':
            reply_id = text_data_json['reply_id']
        else:
            reply_id = None
        if user and user.is_authenticated:
            # Send the message to the group
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message_type': message_type,
                    'message': message,
                    'message_id': message_id,
                    'is_reply': is_reply,
                    'reply_id': reply_id,
                    'username': user.username,
                }
            )
    
    def chat_message(self, event):
        # Accessing sent data
        message = event['message']
        message_type = event['message_type']
        message_id = event['message_id']
        is_reply = event['is_reply']
        reply_id = event['reply_id']
        username = event['username']

        # Getting relevant database objects
        user = User.objects.get(username=username)
        user_stats = UserStats.objects.get(user=user)
        user_pfp_url = user_stats.pfp.url
        if message_type == 'text':
            # Formatting of the timezone when message is displayed on the screen
            local_timezone = pytz.timezone("Australia/Sydney")
            local_datetime = Message.objects.latest('sent_at').sent_at.astimezone(local_timezone)
    
            formatted_datetime = local_datetime.strftime("%B %d, %Y, %I:%M %p").lower().replace('am', 'a.m.').replace('pm', 'p.m.')
            formatted_datetime_capitalized = formatted_datetime.capitalize()
        else:
            formatted_datetime_capitalized = None  # Ensure this variable is defined
        
        # Sending relevant data over
        if is_reply == 'true':
            reply_message = Message.objects.get(id=reply_id)
            self.send(text_data=json.dumps({
                'type': 'incoming_reply_text_message',
                'message_type': message_type,
                'message': message,
                'message_id': message_id,
                'is_reply': is_reply,
                'reply_message': reply_message.text,
                'reply_message_user': reply_message.sender.user.username,
                'reply_id': reply_message.pk,
                'username': user.username,
                'sent_at': formatted_datetime_capitalized,
                'user_pfp_url': user_pfp_url
            }))
        else:
            self.send(text_data=json.dumps({
                'type': 'incoming_text_message',
                'message_type': message_type,
                'message': message,
                'message_id': message_id,
                'is_reply': is_reply,
                'username': user.username,
                'sent_at': formatted_datetime_capitalized,
                'user_pfp_url': user_pfp_url
            }))

class NotificationConsumer(WebsocketConsumer):
    connected_users = {}

    def connect(self):
        user = self.scope["user"] # gets user acessing the consumer class
        user_stats = UserStats.objects.get(user=user)
        self.connected_users[self.channel_name] = user_stats.user
        chat_rooms = ChatRoom.objects.filter(users = user_stats) # gets all chatrooms that the user is invited in
        self.room_group_names = [] # keeps track of all of the chatrooms that will be connected to
        for chat_room in chat_rooms:  
            self.room_group_name = f'notification-stream-{chat_room.pk}' # name is unique to the chatroom's id
            self.room_group_names.append(self.room_group_name)
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            
        self.accept() # connect
            

    def disconnect(self, close_code):
        self.connected_users.pop(self.channel_name)
        for room_name in self.room_group_names: # loops though all connected chatrooms
            async_to_sync(self.channel_layer.group_discard)(
                room_name,
                self.channel_name
            )

    def receive(self, text_data):

        # getting relevant data over to the consumer class
        text_data_json = json.loads(text_data)
        notification_ids = text_data_json['notification_ids']

        # user_on_page_stats = UserStats.objects.get(user=self.scope['user'])
        # if ChatRoom.objects.filter(id=chat_room_id, users=user_on_page_stats).exists():
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_notification',
                'notification_ids': notification_ids,
            }
        )

    def chat_notification(self, event):
        notification_ids = event['notification_ids']
        for notification_id in notification_ids:
            notification = Notification.objects.get(id=notification_id)
            if notification.user.user.username == self.connected_users[self.channel_name].username:
                new_notification = notification
                sender_userstats = UserStats.objects.get(user=User.objects.get(username=new_notification.sender))
                # For the datetime such that it looks neater when displayed
                local_timezone = pytz.timezone("Australia/Sydney")
                local_datetime = new_notification.time_stamp.astimezone(local_timezone)
                formatted_datetime = local_datetime.strftime("%B %d, %Y, %I:%M %p").lower().replace('am', 'a.m.').replace('pm', 'p.m.')
                formatted_datetime_capitalized = formatted_datetime.capitalize()
                notification_timestamp = formatted_datetime_capitalized

                # For the notification icon
                notification_count = Notification.objects.filter(user=new_notification.user).count()

                html_notification_popup = f'''
                <div id="popup-notification-{new_notification.pk}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                    <div class="toast-header">
                        <button class="btn p-0" onclick="location.href='/chat/{new_notification.source.name}/{new_notification.source.pk}'" id="read-notification-{new_notification.pk}">
                            <img src="{new_notification.source.icon.url}" class="rounded me-2" alt="..." style="height: 2.5rem; width: 2.5rem">
                        </button>
                        <button class="btn p-0 pe-2" onclick="location.href='/chat/{new_notification.source.name}/{new_notification.source.pk}'" id="read-notification-{new_notification.pk}">
                            <strong class="me-auto">{new_notification.source.name}</strong>
                        </button>
                        <small class="text-muted pe-2">just now</small>
                        <button type="button ms-2" class="btn-close" id="close-notification-{new_notification.pk}" data-bs-dismiss="toast" aria-label="Close"></button>
                    </div>
                    <div class="toast-body">
                        <div class="row">
                            <div class="col">
                                <img src="{sender_userstats.pfp.url}" class="rounded me-2" alt="" style="height: 2.5rem; width: 2.5rem">
                                <em>{sender_userstats.user.username}</em>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col mt-2">
                                <p class="text-truncate ">{new_notification.contents}</p>
                            </div>
                        </div>
                    </div>
                </div>
                '''

                stored_html_notification = f'''
                <div id="stored-notification-{new_notification.pk}" class="card mb-2" aria-live="assertive" aria-atomic="true" data-bs-autohide="false">
                    <div class="card-header">
                        <button class="btn p-0" onclick="location.href='/chat/{new_notification.source.name}/{new_notification.source.pk}'" id="read-notification-{new_notification.pk}">
                            <img src="{new_notification.source.icon.url}" class="rounded me-2" alt="" style="height: 2.5rem; width: 2.5rem">
                        </button>
                        <button class="btn p-0 pe-2"  onclick="location.href='/chat/{new_notification.source.name}/{new_notification.source.pk}'" id="read-notification-{new_notification.pk}">
                            <strong class="me-auto">{new_notification.source.name}</strong>
                        </button>
                        <small class="text-muted pe-2">{notification_timestamp}</small>
                        <button type="button ms-2" class="btn-close" id="close-notification-{new_notification.pk}" aria-label="Close"></button>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col">
                                <img src="{sender_userstats.pfp.url}" class="rounded me-2" alt="" style="height: 2.5rem; width: 2.5rem">
                                <em>{sender_userstats.user.username}</em>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col mt-2">
                                <p class="text-truncate ">{new_notification.contents}</p>
                            </div>
                        </div>
                    </div>
                </div>
                '''
                notification_id = new_notification.pk

                self.send(text_data=json.dumps({
                    'type': 'incoming_notification',
                    'html_notification_popup': html_notification_popup,
                    'stored_html_notification': stored_html_notification,
                    'notification_id': notification_id,
                    'notification_count': notification_count,
                    'receiver': new_notification.user.user.username,
                    'source_name': new_notification.source.name,
                }))