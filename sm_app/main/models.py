from django.db import models
from django.contrib.auth.models import User
from sm_app import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
import os

def get_image_upload_path_posts(instance, filename):
    
    # Return the full upload path
    return os.path.join(instance.user.username, 'posts/', filename)

def get_image_upload_path_profile(instance, filename):

    return os.path.join(instance.user.username, 'profile/', filename)

# Fields that have only one parent, parent can have only 1 child
class LikedBy(models.Model):
    name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name

class Following(models.Model):
    subscribers = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.subscribers


# models
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    title = models.CharField(max_length=150)
    contents = models.TextField()
    likes = models.IntegerField()
    media = models.ImageField(null=True, upload_to=get_image_upload_path_posts)
    liked_by = models.ManyToManyField(LikedBy)
    created_at = models.DateTimeField()
    date_modified = models.DateTimeField(null=True, default=None)

    def __str__(self):
        return self.title 

class UserStats(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    followers = models.IntegerField()
    pfp = models.ImageField(null=True, upload_to=get_image_upload_path_profile)
    banner = models.ImageField(null=True, upload_to=get_image_upload_path_profile)
    following = models.ManyToManyField(Following)

# Comment Models   
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=600)
    likes = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    liked_by = models.ManyToManyField(LikedBy)

    def __str__(self):
        return f'Comment For {self.post} By {self.user}' 

class NestedComment(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=600)
    likes = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    liked_by = models.ManyToManyField(LikedBy)

    def __str__(self):
        return f'Reply by {self.user} in {self.comment}' 
