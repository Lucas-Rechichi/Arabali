import os

from django.db import models
from main.models import UserStats
# Create your models here.

# To direct the images from user imput into their respective folders.
def get_image_upload_path_room(instance, filename):
    
    # Return the full upload path
    return os.path.join('Rooms/', instance.name, 'room_images/' , filename)

def get_image_upload_path_message(instance, filename):

    return os.path.join('Rooms/', instance.room.name , 'message_images/' , instance.sender.user.username , filename)

def get_video_upload_path_message(instance, filename):

    return os.path.join('Rooms/', instance.room.name , 'message_videos/' , instance.sender.user.username , filename)

class ChatRoom(models.Model):
    name = models.CharField(max_length=150)
    icon = models.ImageField(null=False, upload_to=get_image_upload_path_room)
    room_bg_image = models.ImageField(upload_to=get_image_upload_path_room)
    users = models.ManyToManyField(UserStats)


class Message(models.Model):
    sender = models.ForeignKey(UserStats, on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    text = models.TextField(null=True)
    image = models.ImageField(null=True, upload_to=get_image_upload_path_message)
    video = models.FileField(null=True, upload_to=get_video_upload_path_message)
    sent_at = models.DateTimeField(auto_now_add=True)