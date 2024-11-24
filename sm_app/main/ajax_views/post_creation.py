import json

from datetime import datetime, date
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from main.extras import approx_display, capitalize_plus, difference, exact_display, modified_reciprocal, remove_last_character
from main.models import Post, Media
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

    new_post = Post(title=title, contents=contents, user=user, likes=0)
    new_post.save()
    media_for_post = Media(post=new_post, media_obj=media, caption='default caption')
    media_for_post.save()

    post_catergory = Algorithum.PostCreations.predict_catergory_request(post=new_post)

    


