from django import forms
from .models import Post

class AddPost(forms.Form):
    title = forms.CharField(label="Title of your post:", max_length=150)
    content = forms.CharField(label="Post contents:", max_length=500)
    image = forms.ImageField(label = "Image:", required=True)

     


class EditProfile(forms.Form):
    username = forms.CharField(label='Username (cannot contain spaces):', max_length=150, required=False)
    profile_picture = forms.ImageField(label='Profile Picture (153x153):', required=False)
    profile_banner = forms.ImageField(label='Banner Image (1053x248):', required=False)

    def __init__(self, *args, **kwargs):
        initial = kwargs.pop('initial', {})
        super(EditProfile, self).__init__(*args, **kwargs)
        self.fields['username'].initial = initial.get('username', None)

