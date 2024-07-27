import json

from datetime import datetime, date
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from main.extras import approx_display, capitalize_plus, difference, exact_display, modified_reciprocal, remove_last_character
from main.models import Comment, LikedBy, NestedComment, Post, UserStats, PostTag, Interest, ICF, InterestInteraction, PostInteraction, Notification, Following
from messaging.models import Message, ChatRoom, PollMessage
from django.core.exceptions import ObjectDoesNotExist
from main.algorithum import Algorithum

def liked(request):
    if request.method == 'POST':
        isLiked = False
        user = request.user.username
        post_id = request.POST.get('post_id')
        try:
            post = Post.objects.get(id=post_id)
            tag = PostTag.objects.get(post=post)

            # Checking if the user has this interest already.
            if Interest.objects.filter(user=request.user, name=tag.name).exists():
                interest = Interest.objects.get(user=request.user, name=tag.name)
            else:
                # making the new interest, it's function, and the initial interaction.
                new_interest = Interest(user=request.user, name=tag.name, value=0, current_increace=0, previous_increace=0, date_of_change=date.today())
                new_interest.save()
                new_interest_function = ICF(a=1, k=1, interest=new_interest, form='Parabolic Truncus')
                new_interest_function.save()
                new_interest.save()
                interest = new_interest

        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=404)
        if post.liked_by.filter(name=user).exists(): # If the user has liked the post already
            liked_by = LikedBy.objects.get(name=user)
            post.likes -= 1

            # Value change
            if tag.value - 3 <= 0:
                tag.value = 0
            else:
                tag.value -= 3
            tag.save()
            if interest.value - 3 <= 0:
                interest.value = 0
            else:
                interest.value -= 3
            interest.save()

            # Keeping a record of the interactions
            post_interaction = PostInteraction(tag=tag, value=-3, type='current')
            interest_interaction = InterestInteraction(interest=interest, value=-3, type='current')
            post_interaction.save()
            interest_interaction.save()

            post.liked_by.remove(liked_by)
            isLiked = False
        else:
            liked_by = LikedBy.objects.get(name=user)
            post.likes += 1
            tag.value += 3
            tag.save()
            interest.value += 3
            interest.save()

            # Keeping a record of the interactions
            post_interaction = PostInteraction(tag=tag, value=3, type='current')
            interest_interaction = InterestInteraction(interest=interest, value=3, type='current')
            post_interaction.save()
            interest_interaction.save()

            post.liked_by.add(liked_by)
            isLiked = True
        
        # Saves
        post.save()
        tag.save()
        interest.save()

        # Alter the algorithum baced on this interaction
        Algorithum.AutoAlterations.predictions(interest=interest, tag=None)
        Algorithum.AutoAlterations.predictions(tag=tag, interest=None)

        return JsonResponse({'likes': post.likes, 'isLiked': isLiked})
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def comment_liked(request):
    if request.method == 'POST':
        # Getting relevent data
        username = request.user.username
        comment_id = request.POST.get('comment_id')
        isLiked = False

        # If the user has liked a comment
        if request.POST.get('comment_type') == 'comment':
            comment = Comment.objects.get(id=comment_id)
            tag = PostTag.objects.get(post=comment.post)
            type = 'comment'

        # If the user has liked a reply
        else:
            comment = NestedComment.objects.get(id=comment_id)
            tag = PostTag.objects.get(post=comment.comment.post)
            type = 'reply'

        # Like and dislike logic
        if comment.liked_by.filter(name=username).exists():
            liked_by = LikedBy.objects.get(name=username)
            comment.likes -= 1

            # Logic for comments
            if type == 'comment':

                # Value change
                if tag.value - 2 <= 0:
                    tag.value = 0
                else:
                    tag.value -= 2
                tag.save()
                interest = Interest.objects.get(user=request.user, name=tag.name)
                if interest.value - 2 <= 0:
                    interest.value = 0
                else:
                    interest.value -= 2
                interest.save()

                # Keeping a record of the interactions
                post_interaction = PostInteraction(tag=tag, value=-2, type='current')
                post_interaction.save()
                interest_interaction = InterestInteraction(interest=interest, value=-2, type='current')
                interest_interaction.save()

            # Logic for replies
            if type == 'reply':

                # Value change
                if tag.value - 1 <= 0: # First comment is the reply, second refers to it's corisponding comment
                    tag.value = 0
                else:
                    tag.value -= 1
                tag.save()

                interest = Interest.objects.get(user=request.user, name=tag.name)
                if interest.value - 1 <= 0:
                    interest.value = 0
                else:
                    interest.value -= 1
                interest.save()

                # Keeping a record of the interactions
                post_interaction = PostInteraction(tag=tag, value=-1, type='current')
                post_interaction.save()
                interest_interaction = InterestInteraction(interest=interest, value=-1, type='current')
                interest_interaction.save()
            
            comment.liked_by.remove(liked_by)
            isLiked = False
        else:
            liked_by = LikedBy.objects.get(name=username)
            comment.likes +=1

            # If the user has liked a comment
            if request.POST.get('comment_type') == 'comment':
                comment = Comment.objects.get(id=comment_id)
                tag = PostTag.objects.get(post=comment.post)
                type = 'comment'

            # If the user has liked a reply
            else:
                comment = NestedComment.objects.get(id=comment_id)
                tag = PostTag.objects.get(post=comment.comment.post)
                type = 'reply'
            
            # Logic for comments
            if type == 'comment':

                # Value change
                tag.value += 2
                tag.save()
                interest = Interest.objects.get(user=request.user, name=tag.name)
                interest.value += 2
                interest.save()

                # Keeping a record of the interactions
                post_interaction = PostInteraction(tag=tag, value=2, type='current')
                post_interaction.save()
                interest_interaction = InterestInteraction(interest=interest, value=2, type='current')
                interest_interaction.save()

            if type == 'reply':

                # Value change
                tag.value += 1
                tag.save()

                interest = Interest.objects.get(user=request.user, name=tag.name)
                interest.value += 1
                interest.save()

                # Keeping a record of the interactions
                post_interaction = PostInteraction(tag=tag, value=1, type='current')
                post_interaction.save()
                interest_interaction = InterestInteraction(interest=interest, value=1, type='current')
                interest_interaction.save()

            comment.liked_by.add(liked_by)
            isLiked = True
        comment.save()

        # Altering of the algorithum
        Algorithum.AutoAlterations.predictions(interest=interest, tag=None)
        Algorithum.AutoAlterations.predictions(tag=tag, interest=None)

        return JsonResponse({'likes': comment.likes, 'isLiked': isLiked})
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def new_comment(request):
    if UserStats.objects.get(user=request.user).can_comment:
        if request.method == 'POST':
            # If the user has actually added text into their comment
            if request.POST.get('text'):
                post_id = request.POST.get('post_id')
                post = Post.objects.get(id=post_id)
                text = request.POST.get('text')
                user_stats = UserStats.objects.get(user=request.user)
                tag = PostTag.objects.get(post=post)

                # If the user has this interest already
                if Interest.objects.filter(user=request.user, name=tag.name).exists():
                    interest = Interest.objects.get(user=request.user, name=tag.name)
                else:
                    new_interest = Interest(user=request.user, name=tag.name, value=0)
                    new_interest.save()
                    interest = new_interest


                # Making the comment
                comment = Comment(post=post, text=text, likes=0, user=request.user, created_at = datetime.now())
                comment.save()

                # Adding points for the comment and the user's interest.
                tag.value += 5
                interest.value += 5
                tag.save()
                interest.save()

                # Keeping a record of the interactions
                post_interaction = PostInteraction(tag=tag, value=5, type='current')
                post_interaction.save()
                interest_interaction = InterestInteraction(interest=interest, value=5, type='current')
                interest_interaction.save()
                
                # Altering of the algorithum
                Algorithum.AutoAlterations.predictions(interest=interest, tag=None)
                Algorithum.AutoAlterations.predictions(tag=tag, interest=None)

                # Sending the comments data over to the HTML document so that it can be displayed inside of the post
                responce = {
                    'user':comment.user.username,
                    'post':comment.post.pk,
                    'text':comment.text,
                    'likes':comment.likes,
                    'created_at':comment.created_at,
                    'liked__by': list(comment.liked_by.all()),
                    'pfp':user_stats.pfp.url,
                    'id':comment.pk
                }
                return JsonResponse(responce)
            else:
                return JsonResponse({'error': 'Invalid request method'}, status=405)
        else:
            return JsonResponse({'Error': 'Invalid form submision.'})
    else:
        return render(request, 'main/error.html', {'issue': 'You cannot comment or reply to comments.'})
    
def new_reply(request):
    if UserStats.objects.get(user=request.user).can_comment:
        if request.method == 'POST':
            tag = PostTag.objects.get(post=Comment.objects.get(id=request.POST.get('comment_id')).post)

            # If the user has this interest already
            if Interest.objects.filter(user=request.user, name=tag.name).exists():
                interest = Interest.objects.get(user=request.user, name=tag.name)
            else:
                new_interest = Interest(user=request.user, name=tag.name, value=0)
                new_interest.save()
                interest = new_interest

            # If the user has actually added text into their comment
            if request.POST.get('text'):
                user = request.user
                comment_id = request.POST.get('comment_id')
                user_pfp = UserStats.objects.get(user=user).pfp.url

                # Making the comment
                comment = Comment.objects.get(id=comment_id)
                reply = NestedComment(user=user, comment=comment, likes=0, created_at=datetime.now(), text=request.POST.get('text'))
                tag.value += 4
                tag.current_increace += 4
                interest.value += 1
                interest.current_increace += 1
                tag.save()
                interest.save()
                reply.save()

                # Sending the comments data over to the HTML document so that it can be displayed inside of the comment
                responce = {
                    'reply_id':reply.pk,
                    'user':reply.user.username,
                    'comment_id':reply.comment.pk,
                    'pfp':user_pfp,
                    'created_at':reply.created_at,
                    'text':reply.text,
                    'likes':reply.likes
                }
                return JsonResponse(responce)
            else:
                return JsonResponse({'error': 'Invalid request method'}, status=405)
        else:
            return render(request, 'main/error.html', {'issue': 'You cannot comment or reply to comments.'})

# If the user scrolls by a post.     
def scrolled_by(request):
    user = request.user
    post_id = request.POST.get('post_id')
    print(post_id)
    post = Post.objects.get(id=post_id)
    tag = PostTag.objects.get(post=post)
    interest = Interest.objects.get(user=user, name=tag.name)
    tag.value += 1
    interest.value += 1
    tag.save()
    interest.save()
    interest_interaction = InterestInteraction(interest=interest, value=1, type='current')
    post_interaction = PostInteraction(tag=tag, value=1, type='current')
    interest_interaction.save()
    post_interaction.save()
    Algorithum.AutoAlterations.predictions(interest=interest, tag=None)
    Algorithum.AutoAlterations.predictions(tag=tag, interest=None)
    return JsonResponse({'post_id': post_id})

def ajax_error(request):
    issue = request.POST.get('issue')
    return render(request, 'main/error.html', {'issue': issue})

def save_location(request):
    user_stats = UserStats.objects.get(user=request.user)
    if request.POST.get('accessing-location') == 'true':
        user_stats = UserStats.objects.get(user=request.user)
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        user_stats.last_recorded_latitude = latitude
        user_stats.last_recorded_longitude = longitude
        if request.POST.get('auto-request') == 'false': # so that auto acessing of location dosent reset the 2 hour delay on acessing modals
            user_stats.last_recorded_location = datetime.now()
        user_stats.save()
    else:
        user_stats.last_recorded_location = datetime.now()
        user_stats.save()
    return JsonResponse({'username': user_stats.user.username})

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
        notification = Notification.objects.get(relevant_message=message, user=receiver_userstats)
        notification_id = notification.pk
    notification.delete()
    response = {}
    return JsonResponse(response)

def realtime_suggestions_manager(request):
    type = request.POST.get('type')
    if type == 'search':
        query = request.POST.get('query')
        answer_catergory = request.POST.get('answer_catergory')

        captialized_query = capitalize_plus(query)
        highest_q_value = len(query) * 2
        suggestions = {
            'exact': {},
            'approx':{}
        }

        if answer_catergory == 'UserStats':
            model_records = UserStats.objects.all()
            if len(query) <= 2:

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
                
            elif len(query) == 2 :
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

                extra_chars = len(query) - 2
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
        user_following_objects = Following.objects.all()

        followers = []
        for follower_object in user_following_objects:
            if user_stats.following.filter(subscribers=follower_object):
                follower_user = User.objects.get(username=follower_object)
                follower_userstats = UserStats.objects.get(user=follower_user)
                followers.append({
                    'username': follower_userstats.user.username,
                    'user_pfp_url': follower_userstats.pfp.url,
                })
        response = {
            'follower_list': followers
        }
        return JsonResponse(response)
    else:
        print(f'invalid type of value {type}')
        return JsonResponse({})