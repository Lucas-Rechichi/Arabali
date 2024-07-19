import pytz
import os

from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from main.models import UserStats, Notification
from messaging.models import ChatRoom, Message, PollMessage, PollOption, PollingChoice, MessageNotificationSetting


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

def change_settings(request):
    # Get the setting type
    setting_type = request.POST.get('setting_type')
    if setting_type:
        if setting_type == 'apply_general': # if we are changing something within the general section of the settings
            # For Notifications:
            chosen_setting = request.POST.get('chosen_setting')
            chat_room_id = request.POST.get('chat_room_id')
            user = request.user

            user_stats = UserStats.objects.get(user=user)
            chat_room = ChatRoom.objects.get(id=chat_room_id)
            message_notification_setting = MessageNotificationSetting.objects.get(user=user_stats, source=chat_room)

            if chosen_setting == 'allow_notifications': # If the chosen setting was to allow notifications
                # Set the chosen setting to 'True', set all other options to 'False'.
                message_notification_setting.allow_all = True
                message_notification_setting.replies_only = False
                message_notification_setting.mute_all = False

            elif chosen_setting == 'replies_only':
                message_notification_setting.allow_all = False
                message_notification_setting.replies_only = True
                message_notification_setting.mute_all = False

            elif chosen_setting == 'mute_notiufications':
                message_notification_setting.allow_all = False
                message_notification_setting.replies_only = False
                message_notification_setting.mute_all = True

            else:
                print(f'invalid choice made of {chosen_setting}')

            message_notification_setting.save()
            print(f'message setting for user: {user_stats.user.username}, has ben changed for notifications, to {chosen_setting}.')
            is_successful = True

        elif setting_type == 'apply_styling':
            chat_room_id = request.POST.get('chat_room_id')
            new_name = request.POST.get('new_name')
            new_icon = request.FILES.get('new_icon')
            new_room_bg_image = request.FILES.get('new_room_bg_image')
            user = request.user

            chat_room = ChatRoom.objects.get(id=chat_room_id)
            user_stats = UserStats.objects.get(user=user)

            if new_name:
                old_name = chat_room.name
                chat_room.name = new_name
                chat_room.save()

                # Changing paths on images for the chatroom
                old_icon = str(chat_room.icon)
                old_icon_object = chat_room.icon
                old_icon_path = os.path.join('arabai_users', 'Rooms', old_name, 'room_images', old_icon)

                os.remove(old_icon_path)

                old_room_bg_image = str(chat_room.room_bg_image)
                old_room_bg_image_object = chat_room.room_bg_image
                old_room_bg_image_path = os.path.join('arabai_users', 'Rooms', old_name, 'room_images', old_room_bg_image)

                os.remove(old_room_bg_image_path)

                # Change message paths
                message_images = {}
                message_videos = {}
                messages = Message.objects.get(room=chat_room)
                for message in messages:
                    if message.image:
                        image_object = message.image
                        message_images[message.pk] = image_object

                        image = str(message.image)
                        image_path = os.path.join('arabali_users', 'Rooms', old_name, 'message_images', image)
                        os.remove(image_path)

                    elif message.video:
                        video_object = message.video
                        message_videos[message.pk] = video_object

                        video = str(message.video)
                        video_path = os.path.join('arabali_users', 'Rooms', old_name, 'message_videos', video)
                        os.remove(video_path)

                # Deleting old directory for chatroom.
                os.remove(f'arabali_users/Rooms/{old_name}')

                # Replacing the new paths with images and videos from this chatroom.
                chat_room.icon = old_room_bg_image_object
                chat_room.save()

                chat_room.icon = old_icon_object
                chat_room.save()

                for message in messages:
                    if message.image:
                        message.image = message_images[message.pk]
                        message.save()

                    elif message.video:
                        message.video = message_videos[message.pk]
                        message.save()

                    else:
                        print('text message')
                    
                print(f'Chatroom name changed from {old_name} to {chat_room.name}.')
            else:
                pass
            if new_icon:
                old_icon_string = str(chat_room.icon)
                old_icon_path = os.path.join('arabai_users', 'Rooms', old_name, 'room_images', old_icon_string)
                os.remove(old_icon_path)

                chat_room.icon = new_icon
                chat_room.save()
                print('Chatroom icon image changed.')
            else:
                pass
            if new_room_bg_image: # changing room BG image
                old_room_bg_image_string = str(chat_room.room_bg_image)
                old_room_bg_image_path = os.path.join('arabai_users', 'Rooms', old_name, 'room_images', old_room_bg_image_string)
                os.remove(old_room_bg_image_path)

                chat_room.room_bg_image = new_room_bg_image
                chat_room.save
                print('Chatroom background image changed.')
            else:
                pass
            
            is_successful = True
            print(f'Styling changed for chatroom {chat_room.name}')
        else:
            print(f'invaid setting type of {setting_type}')
            is_successful = False
    else:
        print('no setting type stated.')
        is_successful = False
    response = {
        'successful': is_successful,
    }
    return JsonResponse(response)

def leave_chatroom(request):
    try:
        room_id = request.POST.get('chat_room_id')
        user = request.user

        user_stats = UserStats.objects.get(user=user)
        chat_room = ChatRoom.objects.get(id=room_id)

        chat_room.users.remove(user_stats)
        chat_room.save()
        valid = True
    except:
        print(f'error removing {user.username} from room with id {room_id}.')
        valid = False
    response = {
        'successful': valid
    }
    return JsonResponse(response)

def admin_settings(request):
    chatroom_id = request.POST.get('chatroom_id')
    chatroom = ChatRoom.objects.get(id=chatroom_id)

    if chatroom.owner.username == request.user.username:
        setting_type = request.POST.get('setting_type')
        if setting_type == 'assign_owner':
            new_owner_userstats_id = request.POST.get('userstats_id')
            new_owner_userstats = UserStats.objects.get(id=new_owner_userstats_id)
            
            chatroom.owner = new_owner_userstats.user
            chatroom.save()
            print(f'user {new_owner_userstats.user.username} is now owner of the chatroom {chatroom.name}.')
        elif setting_type == 'remove_users':
            remove_userstats_id_list = request.POST.get('userstats_id_list')
            print(remove_userstats_id_list)
            for userstats_id in remove_userstats_id_list:
                user_stats = UserStats.objects.get(id=userstats_id)
                chatroom.users.remove(user_stats)
                chatroom.save()
                print(f'removed user {user_stats.user.username} from chatroom {chatroom.name}')
        else:
            print('invalid setting type.')
        response = {}
        return JsonResponse(response)
    else:
        print('incorrect user. Only owners can access this setting.')
        return JsonResponse({})