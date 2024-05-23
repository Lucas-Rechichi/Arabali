from django import forms
from .models import Post

class AddPost(forms.Form):
    title = forms.CharField(label="Title of your post:", max_length=150)
    content = forms.CharField(label="Post contents:", max_length=2000)
    image = forms.ImageField(label = "Media (1053x248):", required=True)
    tag = forms.CharField(label='Tag:', required=True, max_length=100)


class Search(forms.Form):
    def __init__(self, *args, **kwargs):
        super(Search, self).__init__(*args, **kwargs)
        self.fields['query'].widget.attrs['id'] = 'searchQuery'

    query = forms.CharField(label='', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Search...'}))


class EditProfile(forms.Form):
    username = forms.CharField(label='Username (cannot contain spaces):', max_length=150, required=False)
    profile_picture = forms.ImageField(label='Profile Picture (153x153):', required=False)
    profile_banner = forms.ImageField(label='Banner Image (1053x248):', required=False)


class EditPost(forms.Form):
    title = forms.CharField(label='New Title:', max_length=150, required=False)
    content = forms.CharField(label='New Content:', max_length=2000, required=False)
    image = forms.FileField(label='New Image:', required=False)

class AddComment(forms.Form):
    def __init__(self, *args, **kwargs):
        super(AddComment, self).__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['id'] = 'comment_text'

    text = forms.CharField(max_length=600)
