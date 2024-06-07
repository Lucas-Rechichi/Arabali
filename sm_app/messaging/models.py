from django.db import models
from main.models import UserStats
# Create your models here.

class ChatRoom(models.Model):
    name = models.CharField(max_length=150)
    icon = models.ImageField(null=False)
    room_bg_image = models.ImageField()
    users = models.ManyToManyField(UserStats)


class Message(models.Model):
    sender = models.ForeignKey(UserStats, on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    text = models.TextField(null=True)
    image = models.ImageField(null=True)
    video = models.FileField(null=True)
    sent_at = models.DateTimeField(auto_now_add=True)