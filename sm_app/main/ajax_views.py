from datetime import datetime
from django.http import JsonResponse
from main.models import Comment, LikedBy, NestedComment, Post, UserStats
from django.core.exceptions import ObjectDoesNotExist

def liked(request):
    if request.method == 'POST':
        isLiked = False
        user = request.user.username
        post_id = request.POST.get('post_id')
        try:
            post = Post.objects.get(id=post_id)
            
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=404)
        if post.liked_by.filter(name=user).exists():
            liked_by = LikedBy.objects.get(name=user)
            post.likes -= 1
            post.liked_by.remove(liked_by)
            isLiked = False
        else:
            liked_by = LikedBy.objects.get(name=user)
            post.likes += 1
            post.liked_by.add(liked_by)
            isLiked = True
        post.save()
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

        # If the user has liked a reply
        else:
            comment = NestedComment.objects.get(id=comment_id)

        # Like and dislike logic
        if comment.liked_by.filter(name=username).exists():
            liked_by = LikedBy.objects.get(name=username)
            comment.likes -=1
            comment.liked_by.remove(liked_by)
            isLiked = False
        else:
            liked_by = LikedBy.objects.get(name=username)
            comment.likes +=1
            comment.liked_by.add(liked_by)
            isLiked = True
        comment.save()
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

            # Making the comment
            comment = Comment(post=post, text=text, likes=0, user=request.user, created_at = datetime.now())
            comment.save()

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
        # If the user has actually added text into their comment
        if request.POST.get('text'):
            user = request.user
            comment_id = request.POST.get('comment_id')
            user_pfp = UserStats.objects.get(user=user).pfp.url

            # Making the comment
            comment = Comment.objects.get(id=comment_id)
            reply = NestedComment(user=user, comment=comment, likes=0, created_at=datetime.now(), text=request.POST.get('text'))
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