import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sm_app.settings')
import django
django.setup()


# Class for all of the methods associated with this connection
import json
import pytz
from datetime import datetime
from urllib.parse import unquote
from main.models import UserStats
from messaging.extras import replace_spaces
from messaging.models import ChatRoom, Message
from django.contrib.auth.models import User

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
        self.room_group_name = f'chat_room_{self.room_id}_{replace_spaces(string=chat_room.name, replacement='_')}'

        # Checking to see if this user has been invited to the chatroom.
        if chat_room.users.filter(user=user_stats.user).exists():
            # Accept the WebSocket connection
            self.accept()
        else:
            # Take action if the user is not on the specific page or is not allowed in the chatroom
            self.close(code=4001)  # Close the connection with a custom error code

        
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
        chat_room_id = text_data_json['chat_room_id']
        message_type = text_data_json['message_type']
        url = unquote(text_data_json['current_url'])
        sender = text_data_json['sender'] # The user who sent the message
        user = self.scope.get("user")  # Use get to safely get the user who is on the page
        
        chat_room = ChatRoom.objects.get(id=chat_room_id)
        print(url)
        if url == f'http://127.0.0.1:8000/chat/{chat_room.name}/{chat_room.pk}': # Change domain name in production
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
                # More discrete notification
        else:
            if user and user.is_authenticated:
                # Send the message to the group
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'chat_notification',
                        'message_type': message_type,
                        'message': message,
                        'user_on_page': user.username,
                        'sender': sender,
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
            # Assuming you want to convert the datetime to a specific timezone
            local_timezone = pytz.timezone("Australia/Sydney")
            local_datetime = Message.objects.latest('sent_at').sent_at.astimezone(local_timezone)
    
            formatted_datetime = local_datetime.strftime("%B %d, %Y, %I:%M %p").lower().replace('am', 'a.m.').replace('pm', 'p.m.')
            formatted_datetime_capitalized = formatted_datetime.capitalize()
        else:
            sent_at = None
        user_pfp_url = user_stats.pfp.url

        # Sending relvant data over
        self.send(text_data=json.dumps({
            'type': 'incoming_message',
            'message_type': message_type,
            'message': message,
            'username': user.username,
            'sent_at': formatted_datetime_capitalized,
            'user_pfp_url': user_pfp_url
        }))

    def chat_notification(self, event):
        # getting relevant data from the recieve function
        message = event['message']
        sender = event['sender']
        message_type = event['message_type']
        timestamp = datetime.now()
