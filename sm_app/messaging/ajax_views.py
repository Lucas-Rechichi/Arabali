
import pytz
import os
import csv
import shutil
import json

import pandas as pd
import google.generativeai as genai

from dotenv import load_dotenv

from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from main.models import UserStats, Notification
from messaging.models import ChatRoom, Message, PollMessage, PollOption, PollingChoice, MessageNotificationSetting, Reaction
from messaging.extras import change_user_directory, emoticons_dict

from sm_app import settings


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

        # updating the csv file when a new message is created.
        csv_path = os.path.join(settings.MEDIA_ROOT, 'conversation_storage', chat_room.name)
        
        if os.path.exists(csv_path):
            pass
        else:
            os.mkdir(csv_path)
        recent_messages = chat_room.messages.all().order_by('-sent_at')[:20]

        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)

        # for rating generation
        genai.configure(api_key=os.getenv('GOOGLE_GEMINI_API_KEY'))
        model = genai.GenerativeModel(model_name='gemini-1.5-flash')
        
        message_dataframe = pd.DataFrame({})
        for message in recent_messages:
            if is_reply == 'true':
                df_is_reply = True
                # reply_to_id is already given a value
            else:
                df_is_reply = False
                reply_to_id = None
            
            new_data = pd.DataFrame({
                'Message Sender': message.sender.user.username,
                'Replied?': df_is_reply,
                'Reply Message ID': reply_to_id,
                'Message Text': message.text if message.text else None,
                'Message Image': message.image.url if message.image else None,
                'Message Video': message.video.url if message.video else None,
                'Message Audio': message.audio.url if message.audio else None,
                'Sent At': message.sent_at
            }, index=[message.pk])
            message_dataframe = pd.concat([message_dataframe, new_data], ignore_index=False)

        message_dataframe.index.name = 'Index (message id)'

        message_dataframe.to_csv(os.path.join(csv_path, 'conversation.csv'), sep=',', na_rep='None')
        message_dataframe = pd.read_csv(os.path.join(csv_path, 'conversation.csv'), sep=',', index_col='Index (message id)')

        if message_dataframe.shape[0] == 0:
            conversation = 'No current messages in this chatroom.'
        else:
            conversation = message_dataframe

        # add rating
        rating = model.generate_content(contents=f"Here is the relevant conversation: {conversation}. Can you rate all of these messages in terms of relevance to the current conversation being held? have your rating be out of ten. Be more leniant with your ratings. Organise these in json data such that it can be trancefered to a python dictionary. Make the keys of the rating the message_id and the values the rating. do not include anything else other than the json data in your response.")
        processed_rating = rating.text.replace("```json", "").replace("```", "")
        processed_rating = eval(processed_rating)

        message_dataframe['Current Conversation Relevance'] = None
        print(processed_rating)

        dropped_indexes = []
        for row_index in range(0, message_dataframe.shape[0]):
            relevance =  processed_rating[f'{message_dataframe.index.values[row_index]}']
            message_dataframe.loc[message_dataframe.index.values[row_index], 'Current Conversation Relevance'] = relevance

            if relevance < 5: # if the relevance is less than 5, cut it out of the conversation memory
                print('below requrement')
                dropped_indexes.append(message_dataframe.index.values[row_index])

        message_dataframe = message_dataframe.drop(index=dropped_indexes)
        message_dataframe.to_csv(os.path.join(csv_path, 'conversation.csv'), sep=',', na_rep='None')

        receivers = chat_room.users.exclude(user=user_stats.user)
        notification_ids = []
        if is_reply == 'true':  # if the message is a reply
            for receiver in receivers:
                message_notification_setting = MessageNotificationSetting.objects.get(user=receiver, source=chat_room)
                if receiver == reply_message.sender: # if the person being replied to happends to be the user that sent the message being replied to.
                    if message_notification_setting.replies_only or message_notification_setting.allow_all:
                        notification_contents = f'({receiver.user.username} Replied To You): {new_message.text}' # special message for the user who created the message being replied to.
                        new_notification = Notification(user=receiver, sender=user_stats.user.username, source=chat_room, contents=notification_contents, relevant_message=new_message)
                        new_notification.save()
                        notification_ids.append(new_notification.id)
                    else:
                        print(f'notification muted for user {receiver.user.username}')
                else:
                    if message_notification_setting.allow_all:
                        new_notification = Notification(user=receiver, sender=user_stats.user.username, source=chat_room, contents=new_message.text, relevant_message=new_message)
                        new_notification.save()
                        notification_ids.append(new_notification.id)
                    else:
                        print(f'notification muted for user {receiver.user.username}')
        else:
            for receiver in receivers:
                message_notification_setting = MessageNotificationSetting.objects.get(user=receiver, source=chat_room)
                if message_notification_setting.allow_all:
                    new_notification = Notification(user=receiver, sender=user_stats.user.username, source=chat_room, contents=new_message.text, relevant_message=new_message)
                    new_notification.save()
                    notification_ids.append(new_notification.id)
                else:
                    print(f'notification muted for user {receiver.user.username}')

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

    # updating the csv file when a new message is created.
    csv_path = os.path.join(settings.MEDIA_ROOT, 'conversation_storage', chat_room.name)

    if os.path.exists(csv_path):
        pass
    else:
        os.mkdir(csv_path)
    recent_messages = chat_room.messages.all().order_by('-sent_at')[:20]

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    # for rating generation
    genai.configure(api_key=os.getenv('GOOGLE_GEMINI_API_KEY'))
    model = genai.GenerativeModel(model_name='gemini-1.5-flash')
    
    message_dataframe = pd.DataFrame({})
    for message in recent_messages:
        if is_reply == 'true':
            df_is_reply = True
            # reply_to_id is already given a value
        else:
            df_is_reply = False
            reply_to_id = None
        
        new_data = pd.DataFrame({
            'Message Sender': message.sender.user.username,
            'Replied?': df_is_reply,
            'Reply Message ID': reply_to_id,
            'Message Text': message.text if message.text else None,
            'Message Image': message.image.url if message.image else None,
            'Message Video': message.video.url if message.video else None,
            'Message Audio': message.audio.url if message.audio else None,
            'Sent At': message.sent_at
        }, index=[message.pk])
        message_dataframe = pd.concat([message_dataframe, new_data], ignore_index=False)

    message_dataframe.index.name = 'Index (message id)'

    if message_dataframe.shape[0] == 0:
        conversation = 'No current messages in this chatroom.'
    else:
        conversation = message_dataframe

    # add rating
    rating = model.generate_content(contents=f"Here is the relevant conversation: {conversation}. Can you rate all of these messages in terms of relevance to the current conversation being held? have your rating be out of ten. Be more leniant with your ratings. Organise these in json data such that it can be trancefered to a python dictionary. do not include anything else other than the json data in your response.")
    processed_rating = rating.text.strip('```json')
    processed_rating = eval(processed_rating)
    
    message_dataframe['Current Conversation Relevance'] = None

    dropped_indexes = []
    for row_index in range(0, message_dataframe.shape[0]):
        relevance =  processed_rating[f'{message_dataframe.index.values[row_index]}']
        message_dataframe.loc[message_dataframe.index.values[row_index], 'Current Conversation Relevance'] = relevance

        if relevance < 5: # if the relevance is less than 5, cut it out of the conversation memory
            print('below requrement')
            dropped_indexes.append(relevance)

    message_dataframe = message_dataframe.drop(index=dropped_indexes)
    message_dataframe.to_csv(os.path.join(csv_path, 'conversation.csv'), sep=',', na_rep='None')

    
    notification_ids = []
    if is_reply == 'true':
        replying_to_id = request.POST.get('replying_to_id')
        reply_message = Message.objects.get(id=replying_to_id)
        new_message = Message(sender=sender_userstats, room=chat_room, image=image, reply=reply_message)
        new_message.save()

        # notification things
        for receiver in receivers:
            message_notification_setting = MessageNotificationSetting.objects.get(user=receiver, source=chat_room)
            if receiver == reply_message.sender: # if the person being replied to happends to be the user that sent the message being replied to.
                if message_notification_setting.replies_only or message_notification_setting.allow_all:
                    notification_contents = f'({receiver.user.username} Replied To You): Image' # special message for the user who created the message being replied to.
                    new_notification = Notification(user=receiver, sender=sender, source=chat_room, contents=notification_contents, relevant_message=new_message)
                    new_notification.save()
                    notification_ids.append(new_notification.id)
                else:
                    print(f'notification muted for user {receiver.user.username}')
            else:
                if message_notification_setting.allow_all:
                    notification_contents = 'Image'
                    new_notification = Notification(user=receiver, sender=sender, source=chat_room, contents=notification_contents, relevant_message=new_message)
                    new_notification.save()
                    notification_ids.append(new_notification.id)
                else:
                    print(f'notification muted for user {receiver.user.username}')

    else:
        new_message = Message(sender=sender_userstats, room=chat_room, image=image)
        new_message.save()

        # notification things
        for receiver in receivers:
            message_notification_setting = MessageNotificationSetting.objects.get(user=receiver, source=chat_room)
            if message_notification_setting.allow_all:
                notification_contents = 'Image'
                new_notification = Notification(user=receiver, sender=sender, source=chat_room, contents=notification_contents, relevant_message=new_message)
                new_notification.save()
                notification_ids.append(new_notification.id)
            else:
                print(f'notification muted for user {receiver.user.username}')

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

    # formatting of the csv file
    csv_path = os.path.join(settings.MEDIA_ROOT, 'conversation_storage', chat_room.name)
    
    if os.path.exists(csv_path):
        pass
    else:
        os.mkdir(csv_path)
    recent_messages = chat_room.messages.all().order_by('-sent_at')[:20]

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    # for rating generation
    genai.configure(api_key=os.getenv('GOOGLE_GEMINI_API_KEY'))
    model = genai.GenerativeModel(model_name='gemini-1.5-flash')
    
    message_dataframe = pd.DataFrame({})
    for message in recent_messages:
        if is_reply == 'true':
            df_is_reply = True
            # reply_to_id is already given a value
        else:
            df_is_reply = False
            reply_to_id = None
        
        new_data = pd.DataFrame({
            'Message Sender': message.sender.user.username,
            'Replied?': df_is_reply,
            'Reply Message ID': reply_to_id,
            'Message Text': message.text if message.text else None,
            'Message Image': message.image.url if message.image else None,
            'Message Video': message.video.url if message.video else None,
            'Message Audio': message.audio.url if message.audio else None,
            'Sent At': message.sent_at
        }, index=[message.pk])
        message_dataframe = pd.concat([message_dataframe, new_data], ignore_index=False)

    message_dataframe.index.name = 'Index (message id)'

    if message_dataframe.shape[0] == 0:
        conversation = 'No current messages in this chatroom.'
    else:
        conversation = message_dataframe

    # add rating
    rating = model.generate_content(contents=f"Here is the relevant conversation: {conversation}. Can you rate all of these messages in terms of relevance to the current conversation being held? have your rating be out of ten. Be more leniant with your ratings. Organise these in json data such that it can be trancefered to a python dictionary. do not include anything else other than the json data in your response.")
    processed_rating = rating.text.strip('```json')
    processed_rating = eval(processed_rating)
    
    message_dataframe['Current Conversation Relevance'] = None

    dropped_indexes = []
    for row_index in range(0, message_dataframe.shape[0]):
        relevance =  processed_rating[f'{message_dataframe.index.values[row_index]}']
        message_dataframe.loc[message_dataframe.index.values[row_index], 'Current Conversation Relevance'] = relevance

        if relevance < 5: # if the relevance is less than 5, cut it out of the conversation memory
            print('below requrement')
            dropped_indexes.append(relevance)

    message_dataframe = message_dataframe.drop(index=dropped_indexes)
    message_dataframe.to_csv(os.path.join(csv_path, 'conversation.csv'), sep=',', na_rep='None')

    notification_ids = []
    if is_reply == 'true':
        replying_to_id = request.POST.get('replying_to_id')
        reply_message = Message.objects.get(id=replying_to_id)
        new_message = Message(sender=sender_userstats, room=chat_room, video=video, reply=reply_message)
        new_message.save()
        # notification things as well
        for receiver in receivers:
            message_notification_setting = MessageNotificationSetting.objects.get(user=receiver, source=chat_room)
            if receiver == reply_message.sender: # if the person being replied to happends to be the user that sent the message being replied to.
                if message_notification_setting.replies_only or message_notification_setting.allow_all:
                    notification_contents = f'({receiver.user.username} Replied To You): Video' # special message for the user who created the message being replied to.
                    new_notification = Notification(user=receiver, sender=sender, source=chat_room, contents=notification_contents, relevant_message=new_message)
                    new_notification.save()
                    notification_ids.append(new_notification.id)
                else:
                    print(f'notification muted for user {receiver.user.username}')
            else:
                if message_notification_setting.allow_all:
                    notification_contents = f'Video'
                    new_notification = Notification(user=receiver, sender=sender, source=chat_room, contents=notification_contents, relevant_message=new_message)
                    new_notification.save()
                    notification_ids.append(new_notification.id)
                else:
                    print(f'notification muted for user {receiver.user.username}')

    else:
        new_message = Message(sender=sender_userstats, room=chat_room, video=video)
        new_message.save()
        
        for receiver in receivers:
            message_notification_setting = MessageNotificationSetting.objects.get(user=receiver, source=chat_room)
            if message_notification_setting.allow_all:
                notification_contents = f'Video'
                new_notification = Notification(user=receiver, sender=sender, source=chat_room, contents=notification_contents, relevant_message=new_message)
                new_notification.save()
                notification_ids.append(new_notification.id)
            else:
                print(f'notification muted for user {receiver.user.username}')
            
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

def message_sent_audio(request):
    # Get data sent over
    audio = request.FILES.get('audio')
    chat_room_id = request.POST.get('chatroom_id')
    is_reply = request.POST.get('is_reply')
    sender = request.user.username

    # Get relevant databace objects
    sender_userstats = UserStats.objects.get(user=User.objects.get(username=sender))
    chat_room = ChatRoom.objects.get(id=chat_room_id)
    receivers = chat_room.users.exclude(user=sender_userstats.user)

    # updating the csv file when a new message is created.
    csv_path = os.path.join(settings.MEDIA_ROOT, 'conversation_storage', chat_room.name)
    
    if os.path.exists(csv_path):
        pass
    else:
        os.mkdir(csv_path)
    recent_messages = chat_room.messages.all().order_by('-sent_at')[:5]
    message_dataframe = pd.DataFrame({})
    for message in recent_messages:
        if is_reply == 'true':
            df_is_reply = True
            # reply_to_id is already given a value
        else:
            df_is_reply = False
            reply_to_id = None
        
        new_data = pd.DataFrame({
            'Message ID': message.pk,
            'Message Sender': message.sender.user.username,
            'Replied?': df_is_reply,
            'Reply Message ID': reply_to_id,
            'Message Text': message.text if message.text else None,
            'Message Image': message.image.url if message.image else None,
            'Message Video': message.video.url if message.video else None,
            'Message Audio': message.audio.url if message.audio else None,
            'Sent At': message.sent_at
        }, index=[message_dataframe.shape[0]])
        message_dataframe = pd.concat([message_dataframe, new_data], ignore_index=True)

        message_dataframe.to_csv(os.path.join(csv_path, 'conversation.csv'), sep=',', na_rep='None')

    notification_ids = []
    if is_reply == 'true':
        replying_to_id = request.POST.get('replying_to_id')
        reply_message = Message.objects.get(id=replying_to_id)
        new_message = Message(sender=sender_userstats, room=chat_room, audio=audio, reply=reply_message)
        new_message.save()
        # notification things as well
        for receiver in receivers:
            message_notification_setting = MessageNotificationSetting.objects.get(user=receiver, source=chat_room)
            if receiver == reply_message.sender: # if the person being replied to happends to be the user that sent the message being replied to.
                if message_notification_setting.replies_only or message_notification_setting.allow_all:
                    notification_contents = f'({receiver.user.username} Replied To You): Audio' # special message for the user who created the message being replied to.
                    new_notification = Notification(user=receiver, sender=sender, source=chat_room, contents=notification_contents, relevant_message=new_message)
                    new_notification.save()
                    notification_ids.append(new_notification.id)
                else:
                    print(f'notification muted for user {receiver.user.username}')
            else:
                if message_notification_setting.allow_all:
                    notification_contents = f'Audio'
                    new_notification = Notification(user=receiver, sender=sender, source=chat_room, contents=notification_contents, relevant_message=new_message)
                    new_notification.save()
                    notification_ids.append(new_notification.id)
                else:
                    print(f'notification muted for user {receiver.user.username}')

    else:
        new_message = Message(sender=sender_userstats, room=chat_room, audio=audio)
        new_message.save()
        
        for receiver in receivers:
            message_notification_setting = MessageNotificationSetting.objects.get(user=receiver, source=chat_room)
            if message_notification_setting.allow_all:
                notification_contents = f'Audio'
                new_notification = Notification(user=receiver, sender=sender, source=chat_room, contents=notification_contents, relevant_message=new_message)
                new_notification.save()
                notification_ids.append(new_notification.id)
            else:
                print(f'notification muted for user {receiver.user.username}')
            
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
        message_notification_setting = MessageNotificationSetting.objects.get(user=receiver_userstats, source=chat_room)
        if message_notification_setting.allow_all:
            new_notification_text = new_poll.title
            new_notification = Notification(sender=request.user.username, user=receiver_userstats, source=chat_room, contents=new_notification_text, relevant_poll=new_poll)
            new_notification.save()
            notification_ids.append(new_notification.pk)
        else:
            print(f'notification muted for user {receiver_userstats.user.username}')

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

            # Getting relevant data
            chat_room_id = request.POST.get('chat_room_id')
            new_name = request.POST.get('new_name')
            new_icon = request.FILES.get('new_icon')
            new_room_bg_image = request.FILES.get('new_room_bg_image')
            user = request.user

            chat_room = ChatRoom.objects.get(id=chat_room_id)

            # checking to see if a new username has been entered.
            if new_name:
                changing_name = new_name
                current_name = chat_room.name

                # Getting and creating old paths and new path strings respectively.
                old_dir_name = chat_room.name
                new_dir_name = changing_name

                old_dir = os.path.join('arabali_users', 'Rooms', old_dir_name)
                new_dir = os.path.join('arabali_users', 'Rooms', new_dir_name)
                
                print(f'New Chatroom Name: {new_name}')

            else:
                changing_name = chat_room.name
                current_name = chat_room.name

                old_dir_name = chat_room.name
                new_dir_name = changing_name

                old_dir = os.path.join('arabali_users', 'Rooms', old_dir_name)
                new_dir = os.path.join('arabali_users', 'Rooms', new_dir_name)
                
                print(f'Current Chatroom Name: {current_name}')

            # Get the current owner of the chatroom
            chatroom_owner = chat_room.owner

            # Saving the users and their notification settings for this chatroom.
            chatroom_users = []
            chatroom_notification_setting_objects = {}
            for user in chat_room.users.all():
                chatroom_users.append(user)
                message_notification_setting = MessageNotificationSetting.objects.get(user=user, source=chat_room)
                chatroom_notification_setting_objects[user.pk] = message_notification_setting

            # Save the messages that were associated with the chatroom.
            main_messages = Message.objects.filter(room=chat_room)
            poll_messages = Message.objects.filter(room=chat_room)

            print('Saving data complete.')

            if new_icon and new_room_bg_image:
                # Both icon and bg image
                print('New icon and BG image.')
                old_icon_path = os.path.join('arabali_users', chat_room.icon.name)
                old_room_bg_image_path = os.path.join('arabali_users', chat_room.room_bg_image.name)

                os.remove(old_icon_path)
                os.remove(old_room_bg_image_path)

                change_user_directory(old_dir, new_dir)

            elif new_icon and not new_room_bg_image:
                print('New icon')
                old_icon_path = os.path.join('arabali_users', chat_room.icon.name)

                old_room_bg_image_path = str(chat_room.room_bg_image)
                new_room_bg_image = old_room_bg_image_path.replace(current_name, changing_name)

                os.remove(old_icon_path)

                change_user_directory(old_dir, new_dir)
            elif not new_icon and new_room_bg_image:
                print('New BG image')
                old_room_bg_image_path = os.path.join('arabali_users', chat_room.room_bg_image.name)
                
                old_icon_path = str(chat_room.icon)
                new_icon = old_icon_path.replace(current_name, changing_name)

                os.remove(old_room_bg_image_path)

                change_user_directory(old_dir, new_dir)
            else:
                print('Neither')

                old_icon_path = str(chat_room.icon)
                new_icon = old_icon_path.replace(current_name, changing_name)

                old_room_bg_image_path = str(chat_room.room_bg_image)
                new_room_bg_image = old_room_bg_image_path.replace(current_name, changing_name)

                change_user_directory(old_dir, new_dir)

            chat_room.delete()

            new_chatroom = ChatRoom(name=changing_name, icon=new_icon, room_bg_image=new_room_bg_image, owner=chatroom_owner)
            new_chatroom.save()

            for user in chatroom_users:
                new_chatroom.users.add(user)
                new_chatroom.save()
                notification_setting = chatroom_notification_setting_objects[user.pk]
                notification_setting.source = new_chatroom
                notification_setting.save()

            for message in main_messages:
                message.room = new_chatroom
                message.save()

            for message in poll_messages:
                message.room = new_chatroom
                message.save()

            is_successful = True
            print(f'Styling changed for chatroom {chat_room.name}')
            response = {
                'successful': is_successful,
                'new_chatroom_id': new_chatroom.pk,
                'new_chatroom_name': new_chatroom.name
            }
            return JsonResponse(response)
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

def invite_users(request):
    chatroom_id = request.POST.get('chatroom_id')
    user_list = json.loads(request.POST.get('user_list'))

    chatroom = ChatRoom.objects.get(id=chatroom_id)

    response_user_list = []
    for user in user_list:
        user_object = User.objects.get(username=user)
        user_stats = UserStats.objects.get(user=user_object)

        chatroom.users.add(user_stats)
        chatroom.save()

        response_user_list.append({
            'username': user,
            'user_pfp_url': user_stats.pfp.url
        })
    message = 'New Users Invited'
    response = {
        'message': message,
        'user_list': response_user_list,
        'user_list_count': len(response_user_list),
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
            message = f'New owner of the chatroom is {new_owner_userstats.user.username}'
            owner_username = new_owner_userstats.user.username
            owner_pfp_url  = new_owner_userstats.pfp.url
            removed_users = None
            removed_user_count = None

        elif setting_type == 'remove_users':
            removed_users = []
            remove_userstats_id_list = json.loads(request.POST.get('userstats_id_list'))

            for userstats_id in remove_userstats_id_list:
                user_stats = UserStats.objects.get(id=userstats_id)
                chatroom.users.remove(user_stats)
                chatroom.save()
                removed_users.append({
                    'username': user_stats.user.username,
                    'user_pfp_url': user_stats.pfp.url,
                })

            print(f'removed user {user_stats.user.username} from chatroom {chatroom.name}')
            message = f'Users have been removed from the chatroom.'
            owner_username = None
            owner_pfp_url = None
            removed_user_count = len(removed_users)

        else:
            print('invalid setting type.')

        response = {
            'message': message,
            'owner_username': owner_username,
            'owner_pfp_url': owner_pfp_url,
            'removed_users': removed_users,
            'removed_user_count': removed_user_count,
        }
        return JsonResponse(response)
    
    else:
        print('incorrect user. Only owners can access this setting.')
        return JsonResponse({})
    
def delete_chatroom(request):
    chatroom_id = request.POST.get('chatroom_id')
    chatroom = ChatRoom.objects.get(id=chatroom_id)
    if chatroom.owner.username == request.user.username:
        messages_in_chatroom = True

        # Getting image paths
        icon_path = os.path.join('arabali_users', chatroom.icon.name)
        room_bg_image_path = os.path.join('arabali_users', chatroom.room_bg_image.name)

        # Deleting images
        try:
            os.remove(icon_path)
            os.remove(room_bg_image_path)
        except OSError or Exception as e:
            print(e)

        # Deleting all images and videos related to messages.
        try:
            messages = Message.objects.get(room=chatroom)
        except ObjectDoesNotExist or Exception as e:
            messages_in_chatroom = False

        if messages_in_chatroom:
            try:
                for message in messages:
                    if message.text:
                        print('Text message')
                    elif message.image:
                        image_path = os.path.join('arabali_users', message.image.name)
                        os.remove(image_path)
                    elif message.video:
                        video_path = os.path.join('arabali_users', message.video.name)
                        os.remove(video_path)
                    else:
                        print('Invalid message type.')

            except OSError or Exception as e:
                print(e)
        else:
            print('No messages in this chatroom.')
            
        # Delete chatroom directory
        chatroom_dir = os.path.join('arabali_users', 'Rooms', chatroom.name)
        try:
            shutil.rmtree(chatroom_dir)
        except FileNotFoundError or Exception as e:
            print(e)

        # Deleting chatroom
        chatroom.delete()
        print(f'chatroom {chatroom.name} with id {chatroom.pk} has been deleted.')
        return JsonResponse({})

    else:
        print('incorrect user. Only owners can access this setting.')
        return JsonResponse({})
    
def edit_message(request):
    message_id = request.POST.get('message_id')
    message_type = request.POST.get('type')

    try:
        message = Message.objects.get(id=message_id)
    except ObjectDoesNotExist as e:
        print(f'No message stored in database with id: {message_id}')
        return None

    if message_type == 'text':
        content = request.POST.get('content')
        if content:
            try:
                message.text = content
                message.edited = True
                message.save()
            except Exception as e:
                print(f'An errror occured: {e}')
                return None

        else:
            print(f'Input content is undefined')
            return None
        
    elif message_type == 'image':
        content = request.FILES.get('content')
        if content:
            file_path = os.path.join(settings.MEDIA_ROOT, message.image.name)
            try:
                os.remove(file_path)
                print(f'OS removed file with path: {file_path}')
            except OSError as e:
                if not file_path:
                    file_path = None

                print(f'OS cannot find the file related to the path {file_path}')
                return None
            
            try:
                message.image = content
                message.edited = True
                message.save()
            except Exception as e:
                print(f'An error occured: {e}')
                return None
            
        else:
            print(f'Input content is undefined')

    elif message_type == 'video':
        content = request.FILES.get('content')
        if content:
            file_path = os.path.join(settings.MEDIA_ROOT, message.video.name)
            try:
                os.remove(file_path)
                print(f'OS removed file with path: {file_path}')
            except OSError as e:
                if not file_path:
                    file_path = None
                print(f'OS cannot find the file related to the path {file_path}')
                return None
            
            try:
                message.video = content
                message.edited = True
                message.save()
            except Exception as e:
                print(f'An error occured: {e}')
                return None
            
        else:
            print(f'Input content is undefined')
    elif message_type == 'audio':
        content = request.FILES.get('content')
        if content:
            file_path = os.path.join(settings.MEDIA_ROOT, message.audio.name)
            try:
                os.remove(file_path)
                print(f'OS removed file with path: {file_path}')
            except OSError as e:
                if not file_path:
                    file_path = None
                print(f'OS cannot find the file related to the path {file_path}')
                return None
            try:
                message.audio = content
                message.edited = True
                message.save()

            except Exception as e:
                print(f'An error occured: {e}')
                return None
        else:
            print(f'Input content is undefined')
            return None
    else:
        print(f'Invalid message type to be editied: {message_type}')
        return None


    response = {
        'message_id': message_id,
        'message_type': message_type,
    }
    return JsonResponse(response)

def delete_message(request):
    message_id = request.POST.get('message_id')
    message_type = request.POST.get('message_type')

    if message_type and message_type == 'general':
        try:
            message = Message.objects.get(id=message_id)

            # Update conversation.csv file
            path = os.path.join(settings.MEDIA_ROOT, 'Rooms', message.room.name, 'message_memory', 'conversation.csv')

            if os.path.isfile(path): # checks to see if the file exists.
                dataframe = pd.read_csv(filepath_or_buffer=path, sep=',', index_col=0)

                if message_id in dataframe.index:
                    new_dataframe = dataframe.drop(index=int(message_id))
                else:
                    new_dataframe = dataframe
                new_dataframe.to_csv(path_or_buf=path, sep=',', na_rep='None')

        except ObjectDoesNotExist or Exception as e:
            print(f'Message with id: {message_id} does not exist.')
            print(f'Error: {e}')
            return None
        
        if message.text:
            message.delete()
        if message.image:
            file_path = os.path.join(settings.MEDIA_ROOT, message.image.name)
        elif message.video:
            file_path = os.path.join(settings.MEDIA_ROOT, message.video.name)
        elif message.audio:
            file_path = os.path.join(settings.MEDIA_ROOT, message.audio.name)
        else:
            print(f'Message with id: {message.pk} has an invalid type.')
        if not message.text:
            try:
                os.remove(file_path)
                message.delete()
            
            except OSError as e:
                print(f'OS could not delete the file at the path: {file_path}')
                return None
            
            except Exception as e:
                print(f'Error: {e}')
                return None
            
    elif message_type and message_type == 'poll':
        try:
            message = PollMessage.objects.get(id=message_id)
            message.delete()
        except ObjectDoesNotExist as e:
            print(f'Poll message with id: {message_id} does not exist.')
            return None
        
        except Exception as e:
            print(f'Error: {e}')
            return None
        
    else:
        print(f'Invalid message type: {message_type}')
        return None
    response = {
        'message_id': message_id,
        'message_type': message_type,
    }
    
    return JsonResponse(response)

def reactions(request):
    # Get relevant data
    message_id = request.POST.get('message_id')
    emoticon = request.POST.get('emoticon')
    user = request.user

    try:
        # Get relevant database objects
        message = Message.objects.get(id=message_id)
        user_stats = UserStats.objects.get(user=user)

        # Check to see if the reaction sent is a valid reaction
        if emoticon in emoticons_dict.keys():
            if message.has_reacted(user=user_stats): # if the user has reacted beforehand
                reaction_obj = Reaction.objects.get(user=user_stats, message=message)
                if message.reactions.filter(user=user_stats, reaction=emoticon).exists(): # if the reaction reacted with was the same reaction as beforhand, deletes reaction
                    reaction_obj.delete()
                    reaction_id = None
                    reaction_result = 'remove'
                else: # replaces a reaction 
                    reaction_obj.reaction = emoticon
                    reaction_obj.save()
                    reaction_id = reaction_obj.pk
                    reaction_result = 'replace'
            else: # creates a reaction
                new_reaction = Reaction(message=message, user=user_stats, reaction=emoticon)
                new_reaction.save()
                reaction_id = new_reaction.pk
                reaction_result = 'new_reaction'
        else:
            print(f'Reaction: {emoticon} is not supported by Arabali.')
            return None

    # Exceptions
    except ObjectDoesNotExist as e:
        if not message.objects.filter(id=message_id).exists():
            print(f'Message with ID: {message_id} does not exist in the database.')
            print(f'An error occured: {e}')
            return None
        else:
            print(f'Object does not exist.')
            print(f'An error occured: {e}')
            return None
        
    # Response
    response = {
        'reaction_result': reaction_result,
        'message_id': message_id,
        'reaction': emoticon,
        'reactor': user.username,
        'reaction_id': reaction_id if reaction_id else None
    }
    return JsonResponse(response)

def message_suggestions(request):
    username = request.POST.get('username')
    chatroom_id = request.POST.get('chatroom-id')

    chatroom = ChatRoom.objects.get(id=chatroom_id)

    load_dotenv()

    google_gemini_api_key = os.getenv('GOOGLE_GEMINI_API_KEY')

    genai.configure(api_key=google_gemini_api_key)
    
    def get_latest_messages(csv_file_path):
        messages = []
        if os.path.isfile(csv_file_path):
            with open(csv_file_path, 'r') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    messages.append(row)  
            return messages[-20:]
        else:
            messages.append('No messages inside the chatroom')
            return messages
    
    data_path = os.path.join(settings.MEDIA_ROOT, 'Rooms', chatroom.name, 'message_memory', 'conversation.csv')

    latest_messages = get_latest_messages(data_path)
    formatted_messages = '\n'.join([' - '.join(message) for message in latest_messages])

    model = genai.GenerativeModel(model_name='gemini-1.5-flash')

    responses = model.generate_content(contents=f"I'm {username} in a chatroom. Here are the lastest messages in the chat, ordered from the newest to the oldest: {formatted_messages}. Please provide three appropriate responses that {username} could say next based on this conversation context. If there are 'No messages inside the chatroom', provide three conversation starters instead. Give them in a python list format, using double quotes for any string content. Only include the suggestions in your response.")

    processed_responses = responses.text.replace("```python", "").replace("```", "")
    processed_responses = eval(processed_responses)

    callback = {
        'responses': processed_responses
    }
    return JsonResponse(callback)
