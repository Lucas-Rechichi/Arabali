import pytz

from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from main.models import UserStats, Notification
from messaging.models import ChatRoom, Message, PollMessage, PollOption, PollingChoice


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
    if text_message and text_message != '':
        if is_reply == 'true': # if the message is a reply
            reply_to_id = request.POST.get('replying-to-id') # get the id of the message being replied to
            reply_message = Message.objects.get(id=reply_to_id) # get the replied message
            new_message = Message(sender=user_stats, room=chat_room, text=text_message, reply=reply_message) # add in the reply into a new message object
            new_message.save()
        else:
            new_message = Message(sender=user_stats, room=chat_room, text=text_message)
            new_message.save()

        receivers = chat_room.users.exclude(user=user_stats.user)
        notification_ids = []
        if is_reply == 'true':  # if the message is a reply
            for receiver in receivers:
                if receiver == reply_message.sender: # if the person being replied to happends to be the user that sent the message being replied to.
                    notification_contents = f'({receiver.user.username} Replied To You): {new_message.text}' # special message for the user who created the message being replied to.
                    new_notification = Notification(user=receiver, sender=user_stats.user.username, source=chat_room, contents=notification_contents, relevant_message=new_message)
                    new_notification.save()
                    notification_ids.append(new_notification.id)
                else:
                    new_notification = Notification(user=receiver, sender=user_stats.user.username, source=chat_room, contents=new_message.text, relevant_message=new_message)
                    new_notification.save()
                    notification_ids.append(new_notification.id)
        else:
            for receiver in receivers:
                new_notification = Notification(user=receiver, sender=user_stats.user.username, source=chat_room, contents=new_message.text, relevant_message=new_message)
                new_notification.save()
                notification_ids.append(new_notification.id)

        # Reformatting of the timezone
        local_timezone = pytz.timezone("Australia/Sydney")
        local_datetime = new_message.sent_at.astimezone(local_timezone)
        
        formatted_datetime = local_datetime.strftime("%B %d, %Y, %I:%M %p").lower().replace('am', 'a.m.').replace('pm', 'p.m.')
        formatted_datetime_capitalized = formatted_datetime.capitalize()

        # Sending JSON responce
        if is_reply == 'true': # Send over specific data over for a reply message
            response = {
                'messageType':'text',
                'is_reply': is_reply,
                'reply_id':new_message.reply.pk,
                'message': new_message.text,
                'message_id': new_message.pk,
                'message_user_pfp_url': new_message.sender.pfp.url,
                'creationDate': formatted_datetime_capitalized,
                'notification_ids': notification_ids,
            }
        else:
            response = {
                'messageType':'text',
                'is_reply': is_reply,
                'message': new_message.text,
                'message_id': new_message.pk,
                'message_user_pfp_url': new_message.sender.pfp.url,
                'creationDate': formatted_datetime_capitalized,
                'notification_ids': notification_ids,
            }
        is_reply = 'false'
        return JsonResponse(response)
    else:
        new_message = Message()
        return JsonResponse({'messageType':'invalid'})


def message_sent_image(request):
    # Get data sent over
    image = request.FILES.get('image')
    chat_room_id = request.POST.get('chat_room_id')
    is_reply = request.POST.get('is_reply')
    sender = request.POST.get('sender')

    sender_userstats = UserStats.objects.get(user=User.objects.get(username=sender))
    chat_room = ChatRoom.objects.get(id=chat_room_id)
    receivers = chat_room.users.exclude(user=sender_userstats.user)
    
    notification_ids = []
    if is_reply == 'true':
        replying_to_id = request.POST.get('replying_to_id')
        reply_message = Message.objects.get(id=replying_to_id)
        new_message = Message(sender=sender_userstats, room=chat_room, image=image, reply=reply_message)
        new_message.save()

        # notification things
        for receiver in receivers:
            if receiver == reply_message.sender: # if the person being replied to happends to be the user that sent the message being replied to.
                notification_contents = f'({receiver.user.username} Replied To You): Image' # special message for the user who created the message being replied to.
                new_notification = Notification(user=receiver, sender=sender, source=chat_room, contents=notification_contents, relevant_message=new_message)
                new_notification.save()
                notification_ids.append(new_notification.id)
            else:
                notification_contents = 'Image'
                new_notification = Notification(user=receiver, sender=sender, source=chat_room, contents=notification_contents, relevant_message=new_message)
                new_notification.save()
                notification_ids.append(new_notification.id)

    else:
        new_message = Message(sender=sender_userstats, room=chat_room, image=image)
        new_message.save()

        # notification things
        for receiver in receivers:
            notification_contents = 'Image'
            new_notification = Notification(user=receiver, sender=sender, source=chat_room, contents=notification_contents, relevant_message=new_message)
            new_notification.save()
            notification_ids.append(new_notification.id)

    # Sending JSON responce
    if is_reply == 'true': # Send over specific data over for a reply message
        response = {
            'messageType':'text',
            'is_reply': is_reply,
            'reply_id':new_message.reply.pk,
            'message_id': new_message.pk,
            'notification_ids': notification_ids,
        }
    else:
        response = {
            'messageType':'text',
            'is_reply': is_reply,
            'message_id': new_message.pk,
            'notification_ids': notification_ids,
        }
    is_reply = 'false'
    return JsonResponse(response)

def message_sent_video(request):
    # Get data sent over
    video = request.FILES.get('video')
    chat_room_id = request.POST.get('chat_room_id')
    is_reply = request.POST.get('is_reply')
    sender = request.POST.get('sender')

    # Get relevant databace objects
    sender_userstats = UserStats.objects.get(user=User.objects.get(username=sender))
    chat_room = ChatRoom.objects.get(id=chat_room_id)
    receivers = chat_room.users.exclude(user=sender_userstats.user)

    notification_ids = []
    if is_reply == 'true':
        replying_to_id = request.POST.get('replying_to_id')
        reply_message = Message.objects.get(id=replying_to_id)
        new_message = Message(sender=sender_userstats, room=chat_room, video=video, reply=reply_message)
        new_message.save()
        # notification things as well
        for receiver in receivers:
            if receiver == reply_message.sender: # if the person being replied to happends to be the user that sent the message being replied to.
                notification_contents = f'({receiver.user.username} Replied To You): Video' # special message for the user who created the message being replied to.
                new_notification = Notification(user=receiver, sender=sender, source=chat_room, contents=notification_contents, relevant_message=new_message)
                new_notification.save()
                notification_ids.append(new_notification.id)
            else:
                notification_contents = f'Video'
                new_notification = Notification(user=receiver, sender=sender, source=chat_room, contents=notification_contents, relevant_message=new_message)
                new_notification.save()
                notification_ids.append(new_notification.id)

    else:
        new_message = Message(sender=sender_userstats, room=chat_room, video=video)
        new_message.save()
        
        for receiver in receivers:
            notification_contents = f'Video'
            new_notification = Notification(user=receiver, sender=sender, source=chat_room, contents=notification_contents, relevant_message=new_message)
            new_notification.save()
            notification_ids.append(new_notification.id)
            
    # Reformatting of the timezone
    local_timezone = pytz.timezone("Australia/Sydney")
    local_datetime = new_message.sent_at.astimezone(local_timezone)
    
    formatted_datetime = local_datetime.strftime("%B %d, %Y, %I:%M %p").lower().replace('am', 'a.m.').replace('pm', 'p.m.')
    formatted_datetime_capitalized = formatted_datetime.capitalize()


    # Sending JSON responce
    if is_reply == 'true': # Send over specific data over for a reply message
        response = {
            'messageType':'text',
            'is_reply': is_reply,
            'reply_id':new_message.reply.pk,
            'message': new_message.text,
            'message_id': new_message.pk,
            'message_user_pfp_url': new_message.sender.pfp.url,
            'creationDate': formatted_datetime_capitalized,
            'notification_ids': notification_ids,
        }
    else:
        response = {
            'messageType':'text',
            'is_reply': is_reply,
            'message': new_message.text,
            'message_id': new_message.pk,
            'message_user_pfp_url': new_message.sender.pfp.url,
            'creationDate': formatted_datetime_capitalized,
            'notification_ids': notification_ids,
        }
    is_reply = 'false'
    return JsonResponse(response)

def create_poll(request):

    print(request.POST)
    # Get sent data
    poll_title = request.POST.get('poll_title')
    chatroom_id = request.POST.get('chatroom_id')
    options = []

    for x in range(1,6):
        option = request.POST.get(f'options_dict[option_{x}]')
        if option is not None:
            options.append(option)
    
    sender = request.user
    sender_userstats = UserStats.objects.get(user=sender)
    chat_room = ChatRoom.objects.get(id=chatroom_id)
    
    new_poll = PollMessage(sender=sender_userstats, room=chat_room, title=poll_title)
    new_poll.save()

    for option in options:
        new_poll_option = PollOption(poll=new_poll, option=option)
        new_poll_option.save()

    notification_ids = []
    for receiver_userstats in chat_room.users.exclude(user=request.user):
        new_notification_text = new_poll.title
        new_notification = Notification(sender=request.user.username, user=receiver_userstats, source=chat_room, contents=new_notification_text, relevant_poll=new_poll)
        new_notification.save()
        notification_ids.append(new_notification.pk)

    response = {
        'poll_id': new_poll.pk,
        'notification_ids': notification_ids,
    }
    return JsonResponse(response)
    
def vote_for_poll(request):

    # Getting relevant data
    option_id = request.POST.get('option_id')
    voter = request.user
    
    # Getting relevant database things
    voter_userstats = UserStats.objects.get(user=voter)
    selected_option = PollOption.objects.get(id=option_id)
    poll = PollMessage.objects.get(id=selected_option.poll.pk)
    other_options = list(poll.options.all())

    # Collectiong all of the polling options
    options = []
    options.append(selected_option)
    for other_option in other_options:
        options.append(other_option)
    
    # Deleting choice created by this user specifically
    for option in options: 
        if PollingChoice.objects.filter(option=option,voter=voter_userstats).exists():
            choice = PollingChoice.objects.get(option=option, voter=voter_userstats)
            choice.delete()

    # Adding in the new choice made
    new_choice = PollingChoice(option=selected_option, voter=voter_userstats)
    new_choice.save()
    
    response = {
        'option_id': option_id
    }
    return JsonResponse(response)