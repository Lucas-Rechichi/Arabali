from django.shortcuts import render

from main.models import UserStats
from messaging.models import ChatRoom, Message
from messaging.extras import get_chat_rooms
from main.extras import initialize_page
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def chat_base(request):
    if UserStats.objects.get(user=request.user).is_banned:
        return render(request, 'main/error.html', {'issue': 'You are banned from Arabali.'})
    chat_rooms = get_chat_rooms(request.user)
    init = initialize_page(request)
    variables = {
        'chat_rooms': chat_rooms,
        'username': init['username'],
        'search_bar': init['search_bar'],
    }
    return render(request, 'messaging/chat_base.html', variables)

@login_required
def chat_room_view(request, room, room_id):
    if UserStats.objects.get(user=request.user).is_banned:
        return render(request, 'main/error.html', {'issue': 'You are banned from Arabali.'})
    # Initialize for HTML
    chat_rooms = get_chat_rooms(request.user)
    init = initialize_page(request)
    
    # Getting relevant database objects
    user = request.user
    rooms = ChatRoom.objects.filter(name=room)
    chat_room = rooms.get(id=room_id)
    user_stats = UserStats.objects.get(user=user)

    # Checking to see if the user has been invited to this chat room.
    if user_stats not in chat_room.users.all():
        return render(request, 'main/error.html', {'issue': 'Cannot access this chatroom.'})
    
    # Getting the messages associated with this chatroom
    messages = Message.objects.filter(room=chat_room)

    # Passing data over to HTML document
    variables = {
        'chat_rooms': chat_rooms,
        'room': chat_room,
        'messages': messages,
        'username': init['username'],
        'search_bar': init['search_bar'],
    }
    return render(request, 'messaging/chat_room_view.html', variables)
