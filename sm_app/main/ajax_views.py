from datetime import datetime, date
from django.http import JsonResponse
from django.shortcuts import render
from main.models import Comment, LikedBy, NestedComment, Post, UserStats, PostTag, Interest, ICF, InterestInteraction, PostInteraction
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
    
def new_reply(request):
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

# If the user scrolls by a post.     
def scrolled_by(request):
    user = request.user
    post_id = request.POST.get('post_id')
    print(post_id)
    post = Post.objects.get(id=post_id)
    tag = PostTag.objects.get(post=post)
    interest = Interest.objects.get(user=user, name=tag.name)
    interest_interaction = InterestInteraction(interest=interest, value=0, type='current')
    post_interaction = PostInteraction(tag=tag, value=0, type='current')
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
    latitude = request.POST.get('latitude')
    longitude = request.POST.get('longitude')
    user_stats.last_recorded_latitude = latitude
    user_stats.last_recorded_longitude = longitude
    user_stats.save()
    return JsonResponse({'username': user_stats.user.username})
