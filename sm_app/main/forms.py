from django import forms
from .models import Post

class AddPost(forms.Form):
    title = forms.CharField(label="Title of your post:", max_length=150)
    content = forms.CharField(label="Post contents:", max_length=500)
    image = forms.ImageField(label = "Image:", required=True)

class EditProfile(forms.Form):
    pass


