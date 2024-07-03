from django import forms

class CreateChatRoom(forms.Form):
    name = forms.CharField(max_length=150)
    icon = forms.ImageField()
    room_bg_image = forms.ImageField(required=False)

