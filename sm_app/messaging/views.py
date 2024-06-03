from django.shortcuts import render
from messaging.extras import get_chat_rooms

from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def chat_base(request):
    chat_rooms = get_chat_rooms(request.user)
    variables = {
        'chat_rooms': chat_rooms
    }
    return render(request, 'messaging/chat_base.html', variables)