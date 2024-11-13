import json

from main.models import UserStats, Post, Comment, NestedComment
from channels.generic.websocket import WebsocketConsumer
from django.core.exceptions import ObjectDoesNotExist

from asgiref.sync import async_to_sync

class PostConsumer(WebsocketConsumer):
    def connect(self):
        # Collects relevant information about the chatroom.
        user = self.scope["user"]

        # Defining the room name
        self.room_group_name = f'post_updates'

        # Add the user to the channel layer
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        # Accept the WebSocket connection
        self.accept()
    
    def disconnect(self, close_code):
        # Remove the WebSocket from the group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
    
    def receive(self, text_data):
        # Accessing sent data
        text_data_json = json.loads(text_data)
        user = self.scope.get("user")  # Use get to safely get the user who is on the page

        request_type = text_data_json['request_type']
        object_id = text_data_json['object_id']
        
        if user and user.is_authenticated:
            # Send the message to the group
            async_to_sync(self.channel_layer.group_send) (
                self.room_group_name,
                {
                    'type': 'posts_manager',
                    'request_type': request_type,
                    'object_id': object_id
                }
            )
    
    def posts_manager(self, event):
        request_type = event['request_type']

        if request_type == 'create_post':
            pass
        elif request_type == 'delete_post':
            pass
        elif request_type == 'create_comment':
            comment_id = event['object_id']

            try:
                comment = Comment.objects.get(id=comment_id)
            except ObjectDoesNotExist:
                print(f'Comment with id: {comment_id} does not exist.')
            except Exception as e:
                print(f'An error occured: {e}')

            user_stats = UserStats.objects.get(user=comment.user)

            data = {
                'text': comment.text,
                'post_id': comment.post.pk,
                'comment_id': comment.pk,
                'username': comment.user.username,
                'user_pfp_url': user_stats.pfp.url
            }

        elif request_type == 'create_reply':
            reply_id = event['object_id']

            try:
                reply = NestedComment.objects.get(id=reply_id)
            except ObjectDoesNotExist:
                print(f'Comment with id: {comment_id} does not exist.')
            except Exception as e:
                print(f'An error occured: {e}')

            user_stats = UserStats.objects.get(user=reply.user)

            data = {
                'text': reply.text,
                'comment_id': reply.comment.pk,
                'reply_id': reply.pk,
                'username': reply.user.username,
                'user_pfp_url': user_stats.pfp.url
            }

        elif request_type == 'update_post_likes':
            post_id = event['object_id']

            try:
                post = Post.objects.get(id=post_id)
            except ObjectDoesNotExist:
                print(f'Post with id: {post_id} does not exist.')
            except Exception as e:
                print(f'An error occured: {e}')
            
            likes = post.likes
            liked_by = post.liked_by
            
            data = {
                'likes': likes,
                'liked_by': liked_by
            }

        elif request_type == 'update_comment_likes':
            pass
        elif request_type == 'update_reply_likes':
            pass
        else:
            print('Invalid request type.')
            return None
        
        self.send(text_data=json.dumps({
            'type': request_type,
            'data': data
        }))
