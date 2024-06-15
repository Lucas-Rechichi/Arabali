from django.shortcuts import render

from main.models import Following, Post, UserStats
from main.algorithum import Algorithum
from messaging.models import ChatRoom, Message
from messaging.forms import CreateChatRoom
from messaging.extras import get_chat_rooms
from main.extras import initialize_page

from django.contrib.auth.models import User
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
        'notifications': init['notification_list'],
        'notification_count': init['notification_count']
    }
    return render(request, 'messaging/chat_room_view.html', variables)

@login_required
def create_chat_room(request, increment):
    if UserStats.objects.get(user=request.user).is_banned:
        return render(request, 'main/error.html', {'issue': 'You are banned from Arabali.'})
    init = initialize_page(request)

    # To be able to choose who to invite to your group
    user_stats = UserStats.objects.get(user=request.user)
    followers = Following.objects.all()
    followed_userstats = []
    user_set = set()
    user_set.add(user_stats.user) # To eliminate the possiblilty of inviting yourself into a chatroom twice

    # Loops though every user that you follow
    for x in followers:
        if user_stats.following.filter(subscribers=x).exists():
            followed_userstats.append(UserStats.objects.get(user=User.objects.get(username=followers.get(subscribers=x))))
            user_set.add(UserStats.objects.get(user=User.objects.get(username=followers.get(subscribers=x))).user)

    # For non-following users
    non_followed_userstats = []
    other_users = UserStats.objects.exclude(user__in=user_set,)
    for other_user in other_users:
        non_followed_userstats.append(other_user)

    # Adding the two lists, with priority towards the users that you follow
    chooseable_users = followed_userstats + non_followed_userstats

    # Limits the page to 9 users per increment
    limited_chooseable_users = []
    for i, user in enumerate(chooseable_users):
        i += 1
        if 0 < i < 10 and increment == 1:
            limited_chooseable_users.append(user)
        elif (10 * (increment - 1)) <= i <= (9 + (10 * (increment - 1))) and increment > 1:
            limited_chooseable_users.append(user)

    # Forms
    if request.method == "POST":
        chat_room_form = CreateChatRoom(request.POST, request.FILES)
        if chat_room_form.is_valid():

            # Getting Values for the creation of the chat room 
            room_name = request.POST.get('name')
            room_icon = request.FILES.get('icon')
            try:
                room_bg_image = request.FILES.get('room_bg_image')
            except:
                room_bg_image = None
                print('No Custom Backround Image Incerted')
            
            # Getting the invited users
            invited_users = []
            possible_ids = list(UserStats.objects.values_list('id', flat=True))
            for id in possible_ids:
                if request.POST.get(f'chosen_user{id}') == f"chosen{id}":
                    relevant_user = UserStats.objects.get(id=id)
                    invited_users.append(relevant_user)

            # Create the chat room
            new_chatroom = ChatRoom(name=room_name, icon=room_icon, room_bg_image=room_bg_image)
            new_chatroom.save()
            invited_users.append(user_stats)
            new_chatroom.users.set(invited_users)
            new_chatroom.save()
    else:
        chat_room_form = CreateChatRoom()

    variables = {
        'username': init['username'],
        'search_bar': init['search_bar'],
        'chat_room_form': chat_room_form,
        'chooseable_users': limited_chooseable_users,
        'increment': {
            'previous': increment - 1,
            'current': increment,
            'next': increment + 1
        },
    }
    return render(request, 'messaging/create_chat_room.html', variables)
