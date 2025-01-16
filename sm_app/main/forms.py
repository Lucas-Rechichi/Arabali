from django import forms

class Search(forms.Form):
    def __init__(self, *args, **kwargs):
        super(Search, self).__init__(*args, **kwargs)
        self.fields['query'].widget.attrs['id'] = 'searchQuery'

    query = forms.CharField(label='', max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Search...'}))


class EditProfile(forms.Form):
    username = forms.CharField(label='Username (cannot contain spaces):', max_length=150, required=False)
    profile_picture = forms.ImageField(label='Profile Picture (153x153):', required=False)
    profile_banner = forms.ImageField(label='Banner Image (1053x248):', required=False)


class EditPost(forms.Form):
    title = forms.CharField(label='New Title:', max_length=150, required=False)
    content = forms.CharField(label='New Content:', max_length=2000, required=False)
    image = forms.FileField(label='New Image:', required=False)

