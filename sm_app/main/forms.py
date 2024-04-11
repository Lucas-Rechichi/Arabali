from django import forms
from .models import Post

class AddPost(forms.Form):
    title = forms.CharField(label="Title of your post:", max_length=150)
    content = forms.CharField(label="Post contents:", max_length=2000)
    image = forms.ImageField(label = "Media: (cannot be changed after upload)", required=True)

     


class EditProfile(forms.Form):
    username = forms.CharField(label='Username (cannot contain spaces):', max_length=150, required=False)
    profile_picture = forms.ImageField(label='Profile Picture (153x153):', required=False)
    profile_banner = forms.ImageField(label='Banner Image (1053x248):', required=False)


class EditPost(forms.Form):
    title = forms.CharField(label='New Title:', max_length=150, required=False)
    content = forms.CharField(label='New Content:', max_length=2000, required=False)
    image = forms.FileField(label='New Image:', required=False)

