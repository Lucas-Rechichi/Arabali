from django.db import models
from main.models import UserStats
# Create your models here.

class ChatRoom(models.Model):
    name = models.CharField(max_length=150)
    icon = models.ImageField(null=False)
    room_bg_image = models.ImageField()
    users = models.ManyToManyField(UserStats)


class TextMessage(models.Model):
    sender = models.OneToOneField(UserStats, on_delete=models.CASCADE)
    receiver = models.OneToOneField(ChatRoom, on_delete=models.CASCADE)
    text = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)


class ImageMessage(models.Model):
    sender = models.OneToOneField(UserStats, on_delete=models.CASCADE)
    receiver = models.OneToOneField(ChatRoom, on_delete=models.CASCADE)
    image = models.ImageField()
    sent_at = models.DateTimeField(auto_now_add=True)


class VideoMessage(models.Model):
    sender = models.OneToOneField(UserStats, on_delete=models.CASCADE)
    receiver = models.OneToOneField(ChatRoom, on_delete=models.CASCADE)
    video = models.FileField()
    sent_at = models.DateTimeField(auto_now_add=True)
        





