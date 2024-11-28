import json

from datetime import datetime, date
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from main.extras import approx_display, capitalize_plus, difference, exact_display, modified_reciprocal, remove_last_character
from main.models import Post, Media, PostTag, Catergory
from messaging.models import Message, ChatRoom, PollMessage
from messaging.extras import emoticons_dict
from django.core.exceptions import ObjectDoesNotExist
from main.algorithum_2 import Algorithum


def add_post(request):

    # Getting sent data
    title = request.POST.get('title')
    contents = request.POST.get('contents')
    media = request.FILES.get('media')
    user = request.user

    # Creating the post and it's media
    new_post = Post(title=title, contents=contents, user=user, likes=0)
    new_post.save()
    media_for_post = Media(post=new_post, media_obj=media, caption='default caption')
    media_for_post.save()

    # Determining the catergory for this post using AI
    post_catergory = Algorithum.PostCreations.predict_catergory_request(post_obj=new_post)

    # Creating the post tag
    tags = PostTag.objects.all()
    tag_values = []
    for tag in tags:
        tag_values.append(tag.value)

    ave_tag_value = Algorithum.Core.average(num_list=tag_values, is_abs=True)
    post_tag = PostTag(post=new_post, name=post_catergory, value=ave_tag_value)
    post_tag.save()
    
    # Creating a new catergory instance if this is a new type of post.
    if not Catergory.objects.filter(name=post_catergory).exists():
        new_catergory = Catergory(name=post_catergory)
        new_catergory.save()

    response = {}

    return JsonResponse(response)


