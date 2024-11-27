import json

from datetime import datetime, date
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from main.extras import approx_display, capitalize_plus, difference, exact_display, modified_reciprocal, remove_last_character
from main.models import Comment, LikedBy, NestedComment, Post, UserStats, PostTag, Interest, ICF, InterestInteraction, PostInteraction, Media
from messaging.models import Message, ChatRoom, PollMessage
from messaging.extras import emoticons_dict
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
                new_interest = Interest(user=request.user, name=tag.name, value=0)
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
        print(request.POST)
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
            comment.save()
        else:
            liked_by = LikedBy.objects.get(name=username)
            comment.likes += 1
            
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
                response = {
                    'user':comment.user.username,
                    'post':comment.post.pk,
                    'text':comment.text,
                    'likes':comment.likes,
                    'created_at':comment.created_at,
                    'liked__by': list(comment.liked_by.all()),
                    'pfp':user_stats.pfp.url,
                    'comment_id':comment.pk
                }
                return JsonResponse(response)
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
                interest.value += 1
                tag.save()
                interest.save()
                reply.save()

                # Keeping a record of the interactions
                post_interaction = PostInteraction(tag=tag, value=4, type='current')
                post_interaction.save()
                interest_interaction = InterestInteraction(interest=interest, value=1, type='current')
                interest_interaction.save()
                
                # Altering of the algorithum
                Algorithum.AutoAlterations.predictions(interest=interest, tag=None)
                Algorithum.AutoAlterations.predictions(tag=tag, interest=None)

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
    if Interest.objects.filter(user=user, name=tag.name):
        interest = Interest.objects.get(user=user, name=tag.name)
    else:
        new_interest = Interest(user=user, name=tag.name, value=0)
        new_interest.save()
        new_interest_interaction = ICF(interest=new_interest, form='Parabolic Truncus', a=0, k=0.1)
        new_interest_interaction.save()
        interest = new_interest
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

# For the location permissions in catch up posts 
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

def load_posts(request):
    increment = request.POST.get('increment')
    catergory = request.POST.get('catergory')
    user = request.user

    new_increment = int(increment) + 1

    posts_to_append = Algorithum.Core.auto_post_loading(incrementing_factor=new_increment, catergory=catergory, user=user)
    posts = {}

    # Loops though all selected posts
    for i, post in enumerate(posts_to_append):
        user_stats = UserStats.objects.get(user=post.user)
        # gets the nested data within comments, liked_by and replies

        # setup
        post_liked_by = {}
        post_media = {}
        post_comments = {}
        post_liked_by_users = list(post.liked_by.all())

        for j in range(0, len(post_liked_by_users)): # liked_by
            # getting relevant data
            user_liked_user_obj = User.objects.get(username=post_liked_by_users[j].name)
            user_liked_userstats = UserStats.objects.get(user=user_liked_user_obj)

            # packaging data into a dictionary
            post_liked_by[j] = {
                'username': post_liked_by_users[j].name,
                'user_pfp_url': user_liked_userstats.pfp.url,
            }
        
        for k, media in Media.objects.filter(post=post):
            post_media[k] = {
                'media_url': media.media_obj.url,
                'caption': media.caption 
            }

        for l, comment in enumerate(post.comments.all()): # comments
            # setup
            post_comment_replies = {}

            for m, reply in enumerate(comment.replies.all()): # replies
                # getting relevant data
                reply_user_userstats = UserStats.objects.get(user=reply.user)

                # if the user has liked this reply
                liked_reply = NestedComment.objects.filter(liked_by=LikedBy.objects.get(name=user.username)).exists()

                # packaging data into a dictionary
                post_comment_replies[m] = { 
                    'reply_id': reply.pk,
                    'reply_username': reply.user.username,
                    'has_liked': liked_reply,
                    'reply_user_pfp_url': reply_user_userstats.pfp.url,
                    'reply_text': reply.text,
                    'reply_likes': reply.likes,
                }
            # getting relevant data
            comment_user_userstats = UserStats.objects.get(user=comment.user)

            # if the user has liked this comment
            liked_comment = Comment.objects.filter(liked_by=LikedBy.objects.get(name=user.username)).exists()

            # packaging data into a dictionary
            post_comments[l] = {
                'comment_id': comment.pk,
                'comment_username': comment.user.username,
                'has_liked': liked_comment,
                'comment_user_pfp_url': comment_user_userstats.pfp.url,
                'comment_text': comment.text,
                'comment_likes': comment.likes,
                'comment_replies': post_comment_replies
            }

        # if the user has liked the post
        liked_post = Post.objects.filter(liked_by=LikedBy.objects.get(name=user.username)).exists()

        # packaging data into a dictionary
        post[i] = {
            'post_id': post.pk,
            'post_username': post.user.username,
            'has_liked': liked_post,
            'post_user_pfp_url': user_stats.pfp.url, 
            'post_title': post.title,
            'post_contents': post.contents,
            'post_media': post_media,
            'post_likes': post.likes,
            'post_media_url': post.media.url,
            'post_created_at': post.created_at,
            'post_liked_by': post_liked_by,
            'post_comments': post_comments
        }

    response = {
        'new_increment': new_increment,
        'posts_to_append': posts,
        'catergory': catergory,
    }

    return JsonResponse(response)
