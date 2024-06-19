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
        sender = text_data_json['sender']  # The user who sent the message
        user = self.scope.get("user")  # Use get to safely get the user who is on the page
        
        chat_room = ChatRoom.objects.get(id=chat_room_id)
        print(url)
        
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

        # Getting relevant database objects
        user = User.objects.get(username=username)
        user_stats = UserStats.objects.get(user=user)
        if message_type == 'text':
            # Assuming you want to convert the datetime to a specific timezone
            local_timezone = pytz.timezone("Australia/Sydney")
            local_datetime = Message.objects.latest('sent_at').sent_at.astimezone(local_timezone)
    
            formatted_datetime = local_datetime.strftime("%B %d, %Y, %I:%M %p").lower().replace('am', 'a.m.').replace('pm', 'p.m.')
            formatted_datetime_capitalized = formatted_datetime.capitalize()
        else:
            formatted_datetime_capitalized = None  # Ensure this variable is defined
        user_pfp_url = user_stats.pfp.url

        # Sending relevant data over
        self.send(text_data=json.dumps({
            'type': 'incoming_message',
            'message_type': message_type,
            'message': message,
            'username': user.username,
            'sent_at': formatted_datetime_capitalized,
            'user_pfp_url': user_pfp_url
        }))

class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        user = self.scope["user"]
        self.room_group_name = 'notification-space'
        self.accept()
        
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['text']
        chat_room_id = text_data_json['chat_room_id']
        message_type = text_data_json['message_type']
        sender = text_data_json['sender']
        csrf_token = text_data_json['csrf_token']
        user = self.scope.get("user")
        
        user_on_page_stats = UserStats.objects.get(user=user)
        if ChatRoom.objects.filter(id=chat_room_id, users=user_on_page_stats).exists():
            if user and user.is_authenticated:
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'chat_notification',
                        'message_type': message_type,
                        'message': message,
                        'receiver': user.username,
                        'sender': sender,
                        'chat_room_id': chat_room_id,
                        'csrf_token': csrf_token
                    }
                )

    def chat_notification(self, event):
        message = event['message']
        sender = event['sender']
        receiver = event['receiver']
        message_type = event['message_type']
        chat_room_id = event['chat_room_id']
        csrf_token = event['csrf_token']

        chat_room = ChatRoom.objects.get(id=chat_room_id)
        user_to_send_to = UserStats.objects.get(user=User.objects.get(username=receiver))
        sender_pfp_url = UserStats.objects.get(user=User.objects.get(username=sender)).pfp.url
        if message_type == 'text':
            new_notification = Notification(user=user_to_send_to, source=chat_room, sender=sender, contents=message)
            new_notification.save()
        else:
            pass

        # For the notification icon
        notification_count = Notification.objects.filter(user=user_to_send_to).count()

        html_notification_popup = f'''
        <div id="popup-notification-{new_notification.pk}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <button class="btn p-0" onclick="location.href='/chat/{chat_room.name}/{chat_room.pk}'" id="read-notification-{new_notification.pk}">
                    <img src="{chat_room.icon.url}" class="rounded me-2" alt="..." style="height: 2.5rem; width: 2.5rem">
                </button>
                <button class="btn p-0 pe-2" onclick="location.href='/chat/{chat_room.name}/{chat_room.pk}'" id="read-notification-{new_notification.pk}">
                    <strong class="me-auto">{chat_room.name}</strong>
                </button>
                <small class="text-muted pe-2">just now</small>
                <button type="button ms-2" class="btn-close" id="close-notification-{new_notification.pk}" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                <div class="row">
                    <div class="col">
                        <img src="{sender_pfp_url}" class="rounded me-2" alt="" style="height: 2.5rem; width: 2.5rem">
                        <em>{sender}</em>
                    </div>
                </div>
                <div class="row">
                    <div class="col mt-2">
                        <p class="text-truncate ">{message}</p>
                    </div>
                </div>
            </div>
        </div>
        '''
        script = '''
        <script>
            $(document).ready(function () {
                $("#close-notification-''' + f'{new_notification.pk}' + '''").click(function () {
                    $.ajax({
                        type: 'POST',
                        url: '/universal/remove-notification/',
                        data: {
                            'csrfmiddlewaretoken': "''' + csrf_token + '''",
                            'notification_id': "''' + f'{new_notification.pk}' + '''",
                        },
                        success: function(response) {
                            console.log(response.message);
                            var notification = $("#''' + f'{new_notification.pk}' + '''");
                            notification.remove();
                            $('#notification-counter').text(response.notification_counter);
                            if (response.notification_count == 0) {
                                $('#notification-counter').remove();
                                $('#bell-icon').removeClass('bi-bell-fill');
                                $('#bell-icon').addClass('bi-bell');
                            }
                        }
                    });
                });

                $("#read-notification-''' + f'{new_notification.pk}' + '''").click(function () {
                    $.ajax({
                        type: 'POST',
                        url: '/universal/remove-notification/',
                        data: {
                            'csrfmiddlewaretoken': "''' + csrf_token + '''",
                            'notification_id': "''' + f'{new_notification.pk}' + '''"
                        },
                        success: function(response) {
                            console.log(response.message);
                        }
                    });
                });
            });
        </script>
        '''

        stored_html_notification = f'''
        <div id="stored-notification-{new_notification.pk}" class="card mb-2" aria-live="assertive" aria-atomic="true" data-bs-autohide="false">
            <div class="card-header">
                <button class="btn p-0" onclick="location.href='/chat/{chat_room.name}/{chat_room.pk}'" id="read-notification-{new_notification.pk}">
                    <img src="{chat_room.icon.url}" class="rounded me-2" alt="" style="height: 2.5rem; width: 2.5rem">
                </button>
                <button class="btn p-0 pe-2"  onclick="location.href='/chat/{chat_room.name}/{chat_room.pk}'" id="read-notification-{new_notification.pk}">
                    <strong class="me-auto">{chat_room.name}</strong>
                </button>
                <small class="text-muted pe-2">{new_notification.time_stamp}</small>
                <button type="button ms-2" class="btn-close" id="close-notification-{new_notification.pk}" aria-label="Close"></button>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col">
                        <img src="{sender_pfp_url}" class="rounded me-2" alt="" style="height: 2.5rem; width: 2.5rem">
                        <em>{sender}</em>
                    </div>
                </div>
                <div class="row">
                    <div class="col mt-2">
                        <p class="text-truncate ">{message}</p>
                    </div>
                </div>
            </div>
        </div>
        '''
        if sender == receiver:
            new_notification.delete()

        self.send(text_data=json.dumps({
            'type': 'incoming_notification',
            'html_notification_popup': html_notification_popup,
            'stored_notification_popup': stored_html_notification,
            'html_script':script,
            'notification_id': new_notification.pk,
            'notification_count': notification_count,
        }))
