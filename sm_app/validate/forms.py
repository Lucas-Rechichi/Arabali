from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class createNewUser(UserCreationForm):
    email = forms.EmailField(max_length=300, widget=forms.TextInput(attrs={'class': 'classA'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']