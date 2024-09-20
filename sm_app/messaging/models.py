import os

from django.db import models
from django.db.models import Count
from django.contrib.auth.models import User
from main.models import UserStats

# Create your models here.

# To direct the images from user imput into their respective folders.
def get_image_upload_path_room(instance, filename):
    return os.path.join('Rooms/', instance.name, 'room_images/' , filename)

def get_image_upload_path_message(instance, filename):
    return os.path.join('Rooms/', instance.room.name , 'message_images/' , instance.sender.user.username , filename)

def get_video_upload_path_message(instance, filename):
    return os.path.join('Rooms/', instance.room.name , 'message_videos/' , instance.sender.user.username , filename)

def get_audio_upload_path_message(instance, filename):
    return os.path.join('Rooms/', instance.room.name , 'message_audio_recordings/' , instance.sender.user.username , filename)

class ChatRoom(models.Model):
    name = models.CharField(max_length=150)
    icon = models.ImageField(null=False, upload_to=get_image_upload_path_room)
    room_bg_image = models.ImageField(upload_to=get_image_upload_path_room)
    users = models.ManyToManyField(UserStats)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

from messaging.extras import emoticons_dict # here due to circular import issues with 'ChatRoom'
class Message(models.Model):
    sender = models.ForeignKey(UserStats, on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    edited = models.BooleanField(default=False, null=False)
    text = models.TextField(null=True)
    image = models.ImageField(null=True, upload_to=get_image_upload_path_message)
    video = models.FileField(null=True, upload_to=get_video_upload_path_message)
    audio = models.FileField(null=True, upload_to=get_audio_upload_path_message)
    sent_at = models.DateTimeField(auto_now_add=True)

    def has_reacted(self, user):
        return Reaction.objects.filter(message=self, user=user).exists()
    


# To let users choose what messages give them a notifitation
class MessageNotificationSetting(models.Model):
    user = models.ForeignKey(UserStats, on_delete=models.CASCADE)
    source = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    allow_all = models.BooleanField(default=True)
    replies_only = models.BooleanField(default=False)
    mute_all = models.BooleanField(default=False)

    def __str__(self):
        return f'Settings for user: {self.user} in group: {self.source}'

# Polling Models
class PollMessage(models.Model):
    sender = models.ForeignKey(UserStats, on_delete=models.CASCADE, null=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, null=False) 
    title = models.CharField(max_length=255, null=False)
    sent_at = models.DateTimeField(auto_now_add=True) 

    def has_voted(self, user):
        return PollingChoice.objects.filter(option__poll=self, voter=user).exists()


class PollOption(models.Model):
    poll = models.ForeignKey(PollMessage, on_delete=models.CASCADE, null=False, related_name='options')
    option = models.CharField(max_length=155, null=False)

class PollingChoice(models.Model):
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE, null=False, related_name='choices')
    voter = models.ForeignKey(UserStats, on_delete=models.CASCADE, null=False)

# Reactions
class Reaction(models.Model):
    user = models.ForeignKey(UserStats, on_delete=models.CASCADE, null=False, related_name='reactions')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, null=False, related_name='reactions')
    reaction = models.CharField(max_length=10, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)

