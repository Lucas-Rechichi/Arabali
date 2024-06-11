import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sm_app.settings')
import django
django.setup()


# Class for all of the methods associated with this connection
import json
from main.models import UserStats
from messaging.models import ChatRoom, Message
from django.contrib.auth.models import User

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class MessageConsumer(WebsocketConsumer):
    def connect(self):
        # Collects relevant information about the chatroom.
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_room_{self.room_id}_{self.room_name}'
        user = self.scope["user"]

        # Getting relevant database objects
        rooms = ChatRoom.objects.filter(name=self.room_name)
        chat_room = rooms.get(id=self.room_id)
        user_stats = UserStats.objects.get(user=user)

        # Checking to see if this user has been invited to the chatroom.
        if chat_room.users.filter(user=user_stats.user).exists():
            # Accept the WebSocket connection
            self.accept()
        
        # Add the WebSocket to the group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

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
        user = self.scope.get("user")  # Use get to safely get the user object

        if user and user.is_authenticated:
            # Send the message to the group
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message_type': message_type,
                    'message': message,
                    'username': user.username,
                }
            )
    
    def chat_message(self, event):
        # Accessing sent data
        message = event['message']
        message_type = event['message_type']
        username = event['username']

        # Getting releevant database objects
        user = User.objects.get(username=username)
        user_stats = UserStats.objects.get(user=user)
        if message_type == 'text':
            sent_at = Message.objects.get(sender=user, text=message).sent_at
        else:
            sent_at = None
        user_pfp_url = user_stats.pfp.url

        # Sending relvant data over
        self.send(text_data=json.dumps({
            'type': 'incoming_message',
            'message_type': message_type,
            'message': message,
            'username': user.username,
            'sent_at': sent_at,
            'user_pfp_url': user_pfp_url
        }))