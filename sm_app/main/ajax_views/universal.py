import json

from datetime import datetime, date
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User

from sm_app import settings
from main.extras import approx_display, capitalize_plus, difference, exact_display, modified_reciprocal, remove_last_character
from main.models import Comment, LikedBy, NestedComment, Post, UserStats, PostTag, Interest, ICF, InterestInteraction, PostInteraction, Notification, Following
from messaging.models import Message, ChatRoom, PollMessage
from messaging.extras import emoticons_dict
from django.core.exceptions import ObjectDoesNotExist
from main.algorithum import Algorithum



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

def check_depreciation_time(request):
    # Getting relevant data
    recieved_timestamp = request.POST.get()
    last_depreciation_timestamp = settings.last_depreciation_timestamp

    # Checking to see if enough time has elapsed (1 day = 86400 seconds)
    if recieved_timestamp - last_depreciation_timestamp >= 86400:

        # Get tags and interests, iterate and apply PCF and ICF respectfuly to them
        tags = PostTag.objects.all()
        interests = Interest.objects.all()

        for tag, interest in tags, interests:
            Algorithum.Depreciations.calculate_post_consequence_function(post_tag_obj=tag)
            Algorithum.Depreciations.calculate_interest_consequence_function(interest_obj=interest)

    

    else:

        # Message to say that the depreciations have occured today
        response = {
            'message': 'Depreciation already occured today'
        }

    return JsonResponse(response)

def realtime_suggestions_manager(request):
    type = request.POST.get('type')
    if type == 'search':
        try:
            abs_cutoff_value = request.POST.get('abs_cutoff_value')
            if abs_cutoff_value == None:
                abs_cutoff_value = 4
        except:
            abs_cutoff_value = 4
        query = request.POST.get('query')
        answer_catergory = request.POST.get('answer_catergory')

        captialized_query = capitalize_plus(query)
        highest_q_value = len(query) * 2
        suggestions = {
            'exact': {},
            'approx': {}
        }

        if answer_catergory == 'UserStats':
            model_records = UserStats.objects.all()
            if len(query) <= abs_cutoff_value:

                # Gets all possible approximate solutions for the inserted query
                approximate_solutions = {}
                broken_query = [x for x in captialized_query] 
                for a in range(len(captialized_query)):
                    approximate_solutions[a + 1] =  broken_query[a]

                for model_record in model_records:
                    split_result_dict = {}
                    split_result_list = [x for x in (model_record.user.username)] 
                    for a in range(len(model_record.user.username)):
                        split_result_dict[split_result_list[a]] =  [a + 1]
                    for combination_id, solution in approximate_solutions.items():
                        if str(solution) in str(model_record.user.username):
                            if model_record.user.pk  not in suggestions['approx'].keys():
                                for char_index, char in approximate_solutions.items():
                                    if char in split_result_list:
                                        combination_id += modified_reciprocal(difference(char_index, split_result_dict[char][0]))
                                suggestions['approx'][model_record.user.pk] = {'id': model_record.user.pk,'name': model_record.user.username, 'value': approx_display(combination_id, highest_q_value), 'user_pfp_url': model_record.pfp.url}

                        if str(solution.lower()) in str(model_record.user.username):
                            if model_record.user.pk  not in suggestions['approx'].keys():
                                for char_index, char in approximate_solutions.items():
                                    if char in split_result_list:
                                        combination_id += modified_reciprocal(difference(char_index, split_result_dict[char][0]))
                                suggestions['approx'][model_record.user.pk] = {'id': model_record.user.pk,'name': model_record.user.username, 'value': approx_display(combination_id, highest_q_value), 'user_pfp_url': model_record.pfp.url}

                sorted_users = sorted(suggestions['approx'].items(), key=lambda item: item[1]['value'], reverse=True)
                suggestions['approx'] = {k: v for k, v in sorted_users}
                solutions = [a for a in suggestions['approx'].values()]
                
            elif len(query) == abs_cutoff_value:
                # Gets all possible exact solutions for the inserted query
                exact_solutions = {}
                changed_query = captialized_query
                for b in range(len(changed_query)):
                    exact_solutions[b + 1] = changed_query
                    changed_query = remove_last_character(changed_query)

                for model_record in model_records:
                    for combination_id, solution in exact_solutions.items():
                        if str(solution) in str(model_record.user.username): # if the string is present within this user's name
                            if model_record.user.pk not in suggestions['exact'].keys(): # Removes duplicates for both exact and approx solutions
                                suggestions['exact'][model_record.user.pk] = {'id': model_record.user.pk,'name': model_record.user.username, 'value': exact_display(modified_reciprocal(combination_id)), 'user_pfp_url': model_record.pfp.url}

                        if str(solution.lower()) in str(model_record.user.username):
                            if model_record.user.pk  not in suggestions['exact'].keys():
                                suggestions['exact'][model_record.user.pk] = {'id': model_record.user.pk,'name': model_record.user.username, 'value': exact_display(modified_reciprocal(combination_id)), 'user_pfp_url': model_record.pfp.url}

                sorted_users = sorted(suggestions['exact'].items(), key=lambda item: item[1]['value'], reverse=True)
                suggestions['exact'] = {k: v for k, v in sorted_users}
                solutions = [e for e in suggestions['exact'].values()]
                print(suggestions)
                
            else:
                # Gets all possible exact solutions for the inserted query. Removes the least likely value every charater over 2.
                exact_solutions = {}
                changed_query = captialized_query
                for b in range(len(changed_query)):
                    exact_solutions[b + 1] = changed_query
                    changed_query = remove_last_character(changed_query)

                extra_chars = len(query) - abs_cutoff_value
                for _ in range(1, extra_chars + 1):
                    exact_solutions.popitem()
                    print(exact_solutions)

                for model_record in model_records:
                    for combination_id, solution in exact_solutions.items():
                        if str(solution) in str(model_record.user.username): # if the string is present within this user's name
                            if model_record.user.pk not in suggestions['exact'].keys(): # Removes duplicates for both exact and approx solutions
                                suggestions['exact'][model_record.user.pk] = {'id': model_record.user.pk,'name': model_record.user.username, 'value': exact_display(modified_reciprocal(combination_id)), 'user_pfp_url': model_record.pfp.url}

                        if str(solution.lower()) in str(model_record.user.username):
                            if model_record.user.pk  not in suggestions['exact'].keys():
                                suggestions['exact'][model_record.user.pk] = {'id': model_record.user.pk,'name': model_record.user.username, 'value': exact_display(modified_reciprocal(combination_id)), 'user_pfp_url': model_record.pfp.url}

                sorted_users = sorted(suggestions['exact'].items(), key=lambda item: item[1]['value'], reverse=True)
                suggestions['exact'] = {k: v for k, v in sorted_users}
                solutions = [e for e in suggestions['exact'].values()]
                print(suggestions)

        elif answer_catergory == 'Emoticons':
            model_records = emoticons_dict.keys()
            if len(query) <= abs_cutoff_value:

                # Gets all possible approximate solutions for the inserted query
                approximate_solutions = {}
                broken_query = [x for x in captialized_query] 
                for a in range(len(captialized_query)):
                    approximate_solutions[a + 1] =  broken_query[a]

                for model_record in model_records:
                    split_result_dict = {}
                    split_result_list = [x for x in (model_record)] 
                    for a in range(len(model_record)):
                        split_result_dict[split_result_list[a]] =  [a + 1]
                    for combination_id, solution in approximate_solutions.items():
                        if str(solution) in str(model_record):
                            if model_record  not in suggestions['approx'].keys():
                                for char_index, char in approximate_solutions.items():
                                    if char in split_result_list:
                                        combination_id += modified_reciprocal(difference(char_index, split_result_dict[char][0]))
                                suggestions['approx'][model_record] = {'name': model_record, 'unicode': emoticons_dict[model_record], 'value': approx_display(combination_id, highest_q_value)}

                        if str(solution.lower()) in str(model_record):
                            if model_record not in suggestions['approx'].keys():
                                for char_index, char in approximate_solutions.items():
                                    if char in split_result_list:
                                        combination_id += modified_reciprocal(difference(char_index, split_result_dict[char][0]))
                                suggestions['approx'][model_record] = {'name': model_record, 'unicode': emoticons_dict[model_record], 'value': approx_display(combination_id, highest_q_value)}

                sorted_users = sorted(suggestions['approx'].items(), key=lambda item: item[1]['value'], reverse=True)
                suggestions['approx'] = {k: v for k, v in sorted_users}
                solutions = [a for a in suggestions['approx'].values()]
                
            elif len(query) == abs_cutoff_value :
                # Gets all possible exact solutions for the inserted query
                exact_solutions = {}
                changed_query = captialized_query
                for b in range(len(changed_query)):
                    exact_solutions[b + 1] = changed_query
                    changed_query = remove_last_character(changed_query)

                for model_record in model_records:
                    for combination_id, solution in exact_solutions.items():
                        if str(solution) in str(model_record): # if the string is present within this user's name
                            if model_record not in suggestions['exact'].keys(): # Removes duplicates for both exact and approx solutions
                                suggestions['exact'][model_record] = {'name': model_record, 'unicode': emoticons_dict[model_record], 'value': approx_display(combination_id, highest_q_value)}

                        if str(solution.lower()) in str(model_record):
                            if model_record  not in suggestions['exact'].keys():
                                suggestions['exact'][model_record] = {'name': model_record, 'unicode': emoticons_dict[model_record], 'value': approx_display(combination_id, highest_q_value)}

                sorted_users = sorted(suggestions['exact'].items(), key=lambda item: item[1]['value'], reverse=True)
                suggestions['exact'] = {k: v for k, v in sorted_users}
                solutions = [e for e in suggestions['exact'].values()]
                print(suggestions)
                
            else:
                # Gets all possible exact solutions for the inserted query. Removes the least likely value every charater over 2.
                exact_solutions = {}
                changed_query = captialized_query
                for b in range(len(changed_query)):
                    exact_solutions[b + 1] = changed_query
                    changed_query = remove_last_character(changed_query)

                extra_chars = len(query) - abs_cutoff_value
                for _ in range(1, extra_chars + 1):
                    exact_solutions.popitem()
                    print(exact_solutions)

                for model_record in model_records:
                    for combination_id, solution in exact_solutions.items():
                        if str(solution) in str(model_record): # if the string is present within this user's name
                            if model_record not in suggestions['exact'].keys(): # Removes duplicates for both exact and approx solutions
                                suggestions['exact'][model_record] = {'name': model_record, 'unicode': emoticons_dict[model_record], 'value': approx_display(combination_id, highest_q_value)}

                        if str(solution.lower()) in str(model_record):
                            if model_record not in suggestions['exact'].keys():
                                suggestions['exact'][model_record] = {'name': model_record, 'unicode': emoticons_dict[model_record], 'value': approx_display(combination_id, highest_q_value)}

                sorted_users = sorted(suggestions['exact'].items(), key=lambda item: item[1]['value'], reverse=True)
                suggestions['exact'] = {k: v for k, v in sorted_users}
                solutions = [e for e in suggestions['exact'].values()]
                print(suggestions)
        else:
            print('invalid catergory to search for.')
        print(sorted_users)
        response = {
            'query_length': len(query),
            'solutions': solutions,
        }
        return JsonResponse(response, safe=False)

    elif type == 'recommend':
        user = request.user
        user_stats = UserStats.objects.get(user=user)
        user_follower_object = Following.objects.get(subscribers=user_stats.user.username)
        followers = UserStats.objects.filter(following=user_follower_object)

        follower_list = []
        for follower in followers:
            follower_list.append({
                'username': follower.user.username,
                'user_pfp_url': follower.pfp.url,
            })
        response = {
            'follower_list': follower_list
        }
        return JsonResponse(response)
    else:
        print(f'invalid type of value {type}')
        return JsonResponse({})
    
