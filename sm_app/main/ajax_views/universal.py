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

def check_depreciation_time(request):
    # Getting relevant data
    recieved_timestamp = int(request.POST.get('timestamp'))
    last_depreciation_timestamp = settings.last_depreciation_timestamp

    # Checking to see if enough time has elapsed (1 day = 86400 seconds)
    if recieved_timestamp - last_depreciation_timestamp >= 86400:

        # Get tags and interests, iterate and apply PCF and ICF respectfuly to them
        tags = PostTag.objects.all()
        interests = Interest.objects.all()

        for tag, interest in zip(tags, interests):
            Algorithum.Depreciations.calculate_post_consequence_function(post_tag_obj=tag)
            Algorithum.Depreciations.calculate_interest_consequence_function(interest_obj=interest)

        # Change the current and old interactions
        current_post_interactions = PostInteraction.objects.filter(is_new=True)
        old_post_interactions = PostInteraction.objects.filter(is_new=False)

        current_interest_interactions = InterestInteraction.objects.filter(is_new=True)
        old_interest_interations = InterestInteraction.objects.filter(ins_new=False)

        for cpi, opi in zip(current_post_interactions, old_post_interactions):
            cpi.is_new = False # new interactions become the old interactions
            cpi.save()
            opi.delete() # delete old interactions

        for cii, oii in zip(current_interest_interactions, old_interest_interations):
            cii.is_new = False # new interactions become the old interactions
            cii.save()
            oii.delete() # delete old interactions

        # Message to say that the depreciations have been successful
        response = {
            'message': 'Depreciation Successful'
        }

    else:

        # Message to say that the depreciations have occured today
        response = {
            'message': 'Depreciation already occured today'
        }

    return JsonResponse(response)

def search_recommendations(request):

    # Getting userstats object
    user_obj = request.user
    userstats_obj = UserStats.objects.get(user=user_obj)

    # Getting recommendations
    post_recommendations = Algorithum.Recommend.recommend_posts(userstats_obj=userstats_obj, max_recommendations=3)
    user_recommendations = Algorithum.Recommend.recommend_users(userstats_obj=userstats_obj, max_recommendations=3)
    category_recommendations = Algorithum.Recommend.recommend_catergories(userstats_obj=userstats_obj, max_recommendations=3)

    response = {
        'post_recommendations': post_recommendations,
        'user_recommendations': user_recommendations,
        'category_recommendations': category_recommendations,
    }

    print(response)

    return JsonResponse(response)


