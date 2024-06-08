from django.http import JsonResponse
from django.shortcuts import render
from main.models import UserStats
from messaging.models import ChatRoom, Message
def message_sent_text(request):
    # Get Relevant User
    user = request.user
    user_stats = UserStats.objects.get(user=user)

    # Get Message Data
    text_message = request.POST.get('text-message')
    chat_room_name = request.POST.get('chat-room-name')
    chat_room_id = request.POST.get('chat-room-id')
    is_reply = request.POST.get('is-reply')

    # Getting Relevant Chatroom
    rooms = ChatRoom.objects.filter(name=chat_room_name)
    chat_room = rooms.get(id=chat_room_id)

    # Creating the new Message and Saving it to the Database
    new_message = Message(sender=user_stats, room=chat_room, text=text_message)
    new_message.save()
    # Sending JSON responce
    responce = {
        'messageType':'text',
        'message': new_message.text,
        'message_user_pfp_url': new_message.sender.pfp.url,
        'creationDate': new_message.sent_at,
    }
    return JsonResponse(responce)


