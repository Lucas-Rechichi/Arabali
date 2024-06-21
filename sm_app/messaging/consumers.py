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

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class MessageConsumer(WebsocketConsumer):

    def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        user = self.scope["user"]

        try:
            chat_room = ChatRoom.objects.get(id=self.room_id)
            user_stats = UserStats.objects.get(user=user)
        except ChatRoom.DoesNotExist:
            self.close(code=4004)  # Close connection if chat room does not exist
            return
        except UserStats.DoesNotExist:
            self.close(code=4004)  # Close connection if user stats do not exist
            return

        self.room_group_name = f'chat_room_{self.room_id}_{replace_spaces(string=chat_room.name, replacement="_")}'

        if chat_room.users.filter(user=user_stats.user).exists():
            self.accept()
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
        else:
            self.close(code=4001)  # Close the connection with a custom error code

    def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['text']
            message_type = text_data_json['message_type']
            user = self.scope.get("user")

            if user and user.is_authenticated:
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message_type': message_type,
                        'message': message,
                        'username': user.username,
                    }
                )
        except json.JSONDecodeError:
            self.close(code=4002)  # Close connection on JSON decode error

        
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

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_authenticated:
            self.room_group_name = f'notification-space-{user.username}'
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close(code=4003)  # Close connection if user is not authenticated

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['text']
        chat_room_id = text_data_json['chat_room_id']
        message_type = text_data_json['message_type']
        sender = text_data_json['sender']
        csrf_token = text_data_json['csrf_token']
        users = await database_sync_to_async(ChatRoom.objects.get)(id=chat_room_id).users.values('user').distinct()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_notification',
                'message_type': message_type,
                'message': message,
                'receivers': list(users),
                'sender': sender,
                'chat_room_id': chat_room_id,
                'csrf_token': csrf_token
            }
        )

    async def chat_notification(self, event):
        message = event['message']
        sender = event['sender']
        receivers = event['receivers']
        message_type = event['message_type']
        chat_room_id = event['chat_room_id']
        csrf_token = event['csrf_token']

        chat_room = await database_sync_to_async(ChatRoom.objects.get)(id=chat_room_id)
        sender_pfp_url = await database_sync_to_async(UserStats.objects.get)(user=await database_sync_to_async(User.objects.get)(username=sender)).pfp.url

        sent_users = set()
        for receiver in receivers:
            receiver_id = receiver['user']
            if receiver_id not in sent_users:
                sent_users.add(receiver_id)
                user = await database_sync_to_async(UserStats.objects.get)(user=await database_sync_to_async(User.objects.get)(id=receiver_id))
                if message_type == 'text':
                    new_notification = await database_sync_to_async(Notification.objects.create)(
                        user=user, source=chat_room, sender=sender, contents=message
                    )

                notification_count = await database_sync_to_async(Notification.objects.filter)(
                    user=user).count()

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
                                    'csrfmiddlewaretoken': "''' + f'{csrf_token}' + '''",
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
                        <button type="button ms-2" class="btn-close" id="close-notification-{new_notification.pk}" data-bs-dismiss="toast" aria-label="Close"></button>
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

                await self.send(text_data=json.dumps({
                    'message_type': message_type,
                    'notification_count': notification_count,
                    'sender': sender,
                    'receiver': user.user.username,
                    'notification_id': new_notification.pk,
                    'html_notification_popup': html_notification_popup,
                    'stored_html_notification': stored_html_notification,
                    'html_script': script
                }))
