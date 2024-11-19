import os

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# To direct the images from user imput into their respective folders.
def get_image_upload_path_posts(instance, filename):
    
    # Return the full upload path
    return os.path.join(instance.user.username, 'posts/', filename)

def get_image_upload_path_profile(instance, filename):

    return os.path.join(instance.user.username, 'profile/', filename)

def get_default_content_type(model):

    return ContentType.objects.get_for_model(model).id

# Fields that have only one parent, parent can have only 1 child
class LikedBy(models.Model):
    name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name

class Following(models.Model):
    subscribers = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.subscribers


# Main models
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    title = models.CharField(max_length=150)
    contents = models.TextField()
    likes = models.IntegerField()
    media = models.ImageField(null=True, upload_to=get_image_upload_path_posts)
    liked_by = models.ManyToManyField(LikedBy, related_name='post_liked_by')
    created_at = models.DateTimeField()
    day_of_creation = models.DateField()
    date_modified = models.DateTimeField(null=True, default=None)

    def __str__(self):
        return self.title 

class UserStats(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    followers = models.IntegerField()
    pfp = models.ImageField(null=True, upload_to=get_image_upload_path_profile)
    banner = models.ImageField(null=True, upload_to=get_image_upload_path_profile)
    following = models.ManyToManyField(Following)
    last_recorded_latitude = models.FloatField(default=50)
    last_recorded_longitude = models.FloatField(default=100)
    last_recorded_location = models.DateTimeField(null=False, auto_now_add=True)
    can_post = models.BooleanField(default=True)
    can_comment = models.BooleanField(default=True)
    is_banned = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

from messaging.models import ChatRoom, Message, PollMessage


# Notifications
class Notification(models.Model):
    user = models.ForeignKey(UserStats, on_delete=models.CASCADE, null=False)
    source = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, null=False)
    relevant_message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True)
    relevant_poll = models.ForeignKey(PollMessage, on_delete=models.CASCADE, null=True)
    relevant_post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    sender = models.CharField(max_length=300)
    contents = models.TextField()
    time_stamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notification for user: {self.user}'

# Comment Models   
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=600)
    likes = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    liked_by = models.ManyToManyField(LikedBy, related_name='comment_liked_by')

    def __str__(self):
        return f'Comment For {self.post} By {self.user}' 

class NestedComment(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=600)
    likes = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    liked_by = models.ManyToManyField(LikedBy, related_name='reply_liked_by')

    def __str__(self):
        return f'Reply by {self.user} in {self.comment}' 


# Algorithum
class Interest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.IntegerField()

    def __str__(self):
        return self.name
    

class PostTag(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=100)
    value = models.IntegerField()

    def __str__(self):
        return self.name
    
# Interest Consequence Function, holds onto parameters for the function.
class ICF(models.Model):
    interest = models.OneToOneField(Interest, on_delete=models.CASCADE, null=False)
    form = models.CharField(max_length=100, null=False)
    a = models.FloatField(null=True)
    k = models.FloatField(null=True)

    def __str__(self):
        return f'Function for {self.interest.name} for user {self.interest.user.username}'
    

# Post Consequence Function, holds onto parameters for the function.
class PCF(models.Model):
    tag = models.OneToOneField(PostTag, on_delete=models.CASCADE, null=False)
    form = models.CharField(max_length=100, null=False)
    a = models.FloatField()
    k = models.FloatField()

    def __str__(self):
        return f'Function for {self.tag.name} for post {self.tag.post.title}'
    
# Interaction Tracking
class InterestInteraction(models.Model):
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE)
    value = models.IntegerField()
    type = models.CharField(max_length=20, null=False) 

    def __str__(self):
        return f'interaction from {self.interest.user} on interest {self.interest}'


class PostInteraction(models.Model):
    tag = models.ForeignKey(PostTag, on_delete=models.CASCADE)
    value = models.IntegerField()
    type = models.CharField(max_length=20, null=False) 
    
    def __str__(self):
        return f'interaction on {self.tag} for tag  {self.tag.name}'
    

# For date and time related things
class DateAndOrTimeSave(models.Model):
    object = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    abstract = models.CharField(max_length=300, null=True)
    day = models.DateField(null=True)
    time = models.TimeField(null=True)
    day_time = models.DateTimeField(null=True)
    

# System related
class ArabaliConfigure(models.Model):
    name = models.CharField(max_length=100)
    allowed = models.BooleanField(default=True)

    def __str__(self):
        return self.name

