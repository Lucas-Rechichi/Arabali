import re
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User

from sm_app import settings
from main.extras import approx_display, capitalize_plus, difference, exact_display, modified_reciprocal, remove_last_character
from main.models import UserStats, PostTag, Interest, InterestInteraction, PostInteraction, Notification, Following
from main.algorithum import Algorithum

from messaging.models import Message, PollMessage
from messaging.extras import emoticons_dict


def ajax_error(request):
    issue = request.POST.get('issue')
    return render(request, 'main/error.html', {'issue': issue})


def remove_notification(request):
    type = request.POST.get('type')
    receiver_user = User.objects.get(username=request.POST.get('receiver'))
    receiver_userstats = UserStats.objects.get(user=receiver_user)
    if type == "notification-id":
        notification_id = request.POST.get('notification_id')
        notification = Notification.objects.get(id=notification_id)
    elif type == "poll_message_id":
        poll_id = request.POST.get('poll_id')
        poll_message = PollMessage.objects.get(id=poll_id)
        notification = Notification.objects.get(relevant_poll=poll_message, user=receiver_userstats)
        notification_id = notification.pk
    else:
        message_id = request.POST.get('message-id')
        message = Message.objects.get(id=message_id)
        print(f'message: {message} for user: {receiver_userstats}.')
        notification = Notification.objects.get(relevant_message=message, user=receiver_userstats)
        notification_id = notification.pk
    notification.delete()
    response = {}
    return JsonResponse(response)

def check_modulation_time(request):
    # Getting relevant data
    recieved_timestamp = int(request.POST.get('timestamp'))
    last_modulation_timestamp = settings.last_modulation_timestamp

    # Checking to see if enough time has elapsed (1 day = 86400 seconds)
    if recieved_timestamp - last_modulation_timestamp >= 86400:

        # Get tags and interests, iterate and apply PCF and ICF respectfuly to them
        tags = PostTag.objects.all()
        interests = Interest.objects.all()

        for tag, interest in zip(tags, interests):
            Algorithum.Modulations.calculate_post_consequence_function(post_tag_obj=tag)
            Algorithum.Modulations.calculate_interest_consequence_function(interest_obj=interest)

        # Change the current and old interactions
        current_post_interactions = PostInteraction.objects.filter(is_new=True)
        old_post_interactions = PostInteraction.objects.filter(is_new=False)

        current_interest_interactions = InterestInteraction.objects.filter(is_new=True)
        old_interest_interations = InterestInteraction.objects.filter(is_new=False)

        for cpi, opi in zip(current_post_interactions, old_post_interactions):
            cpi.is_new = False # new interactions become the old interactions
            cpi.save()
            opi.delete() # delete old interactions

        for cii, oii in zip(current_interest_interactions, old_interest_interations):
            cii.is_new = False # new interactions become the old interactions
            cii.save()
            oii.delete() # delete old interactions

        # Change the time set in settings for the modulation timestamp to the current timestamp
        current_timestamp = round(datetime.now().timestamp())
        timestamp_syntax = f'last_modulation_timestamp = {current_timestamp}'
        settings_file_path = 'sm_app/settings.py'

        with open(settings_file_path, 'r') as settings_file: # read file, get data
            file_content = settings_file.read()

        variable_syntax_pattern = r'(last_modulation_timestamp\s*=\s*)\d+' # syntax pattern
        updated_file_content = re.sub(variable_syntax_pattern, rf'{timestamp_syntax}', file_content) # replace with new timestamp
        
        with open(settings_file_path, 'w') as settings_file: # write the file again
            settings_file.write(updated_file_content)

        # Message to say that the modulations have been successful
        response = {
            'message': 'Modulations Successful'
        }

    else:

        # Message to say that the modulations have occured today
        response = {
            'message': 'Modulations already occured today'
        }

    return JsonResponse(response)

def search_recommendations(request):

    # Getting userstats object
    user_obj = request.user
    userstats_obj = UserStats.objects.get(user=user_obj)

    # Getting recommendations
    user_recommendations = Algorithum.Recommend.recommend_users(userstats_obj=userstats_obj, max_recommendations=3)
    category_recommendations = Algorithum.Recommend.recommend_catergories(userstats_obj=userstats_obj, max_recommendations=3)

    response = {
        'user_recommendations': user_recommendations,
        'category_recommendations': category_recommendations,
    }

    return JsonResponse(response)

def search_suggestions(request):
    query = request.POST.get('query')
    highest_q_value = len(query) * 2

    solutions_data = Algorithum.Search.query_solutions(query=query, abs_cutoff_value=4)
    solution_type = solutions_data['type']

    results_dict = {
        'exact': {
            'users': [],
            'categories': [],
        },
        'approx' : {
            'users': [],
            'categories': [],
        }
    }

    id_dict = {}

    # Searches for apropriate solutions given the query 
    results_dict = Algorithum.Search.result_values_users(results_dict=results_dict, solutions_data=solutions_data, id_dict=id_dict, highest_q_value=highest_q_value)
    results_dict = Algorithum.Search.result_values_categories(results_dict=results_dict, solutions_data=solutions_data, id_dict=id_dict, highest_q_value=highest_q_value)

    # Solution sorting
    results_dict = Algorithum.Search.query_sorting(results_dict=results_dict, search_type=solution_type)

    # Extract relevant data from search results so that they can be serialized though JSON to the front-end.
    results_data = {
        'users': [],
        'categories': []
    }

    for index, user_solution in enumerate(results_dict[solution_type]['users']):
        if index < 3:
            results_data['users'].append({
                'username': user_solution['object'].user.username,
                'user_pfp_url': user_solution['object'].pfp.url
            })
        else:
            break

    for index, category_solution in enumerate(results_dict[solution_type]['categories']):
        if index < 3:
            results_data['categories'].append({
                'category_name': category_solution['object'].name
            })
        else:
            break

    print(results_data)

    response = {
        'results_data': results_data
    }

    return JsonResponse(response)








